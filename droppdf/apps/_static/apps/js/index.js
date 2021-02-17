var myDropzone;
var addedFile = 0;
var fileObj;
var filename = "";
var ocr_progress;
var ocr_progress_status = 0;
var estimated_time = 0;

var type = "";

//Google Drive Authentication
function handleAuthClick(event) {
    //give notice if auth keys not present
    if (CLIENT_ID == '' ||  API_KEY == '' || SCOPES == []) {
        alert('Google authorization keys not present. Check configs exist.');
        return;
    }
    gapi.auth.authorize(
            {client_id: CLIENT_ID,
            scope: SCOPES.join(' '),
            immediate: false},
            handleauthresult);
    return false;
};

function handleauthresult(authresult) {
    if (authresult && !authresult.error) {
        //auth was successful.
        //open google drive in new tab
        var d = document.createElement('a');
        d.id = 'open-google-drive';
        d.href = 'https://drive.google.com/drive/my-drive';
        d.target = '_blank';
        document.body.appendChild(d);
        d.click();

        //window.open('https://drive.google.com/drive/my-drive', '_blank');
    } else {
        //auth failed
        return;
    }
}

$(document).ready(function(){
    var valid_extensions = ['pdf', 'docx', 'xlsx', 'doc', 'xls', 'csv', 'epub'];

    var options = {
        url: "/upload/",
        headers: {
        'x-csrftoken': CSRF_TOKEN
        },

        paramName: "file",

        timeout: 120000,

        clickable: false,

        uploadprogress: function(file, progress, bytes) {
            //account for upload from server to cloud
            var width = progress * .66;

            $('[data-dz-uploadprogress]').css('width', width + '%');

            //there is lag between full upload and complete because of upload 
            //time from server to cloud. in process.
            //complete progressbar
            if (progress >= 100) {
                $('#process-content-text')
                    .text('Processing...')

                var intvl = setInterval(function() {
                    if (width >= 100) {
                        clearInterval(intvl);
                        return;
                    };
                    width += 1;
                    $('[data-dz-uploadprogress]').css('width', width + '%');
                }, 150);
            };
        },

        accept: function(file, done) {
            $("#progressbar").show();

            fileObj = file;

            $('#main-content-text').hide();

            $('#process-content-text')
                .text('Uploading...')
                .show();

            done();
        },

        init: function() {
            this.on("addedfile", function(file) {
                var extention = file.name.split(".");
                extention = extention[extention.length-1];
                extention = extention.toLowerCase();
            
                var valid_extensions = ['pdf', 'docx', 'xlsx', 'doc', 'xls', 'csv', 'epub'];
                
                if (valid_extensions.includes(extention)) {
                    type = extention
                    if (addedFile == 0) {
                        addedFile = 1;
                    }
                    else {
                        this.removeFile(file);
                    }
                }
                else {
                    setTimeout(function() {
                        //filetype error
                    }, 700);

                    this.removeFile(file);
                }
            });

            this.on("success", function(file, filename) {
                $('[data-dz-uploadprogress]').css('width', '100%');

                if (filename == 'pdf has no text or is image pdf') {
                    alert('image pdf');
                };

                return;

                if(type == 'pdf') {
                    window.location.href = '/pdf/' + filename + '/'
                };
            });

            this.on("error", function(file, error, xhr) {

                /* if 406 "Not Acceptable" pdf has no text */
                if (xhr.status == 406) {
                    var html = 'error'; 

                    displayError(html);
                };

            });

            this.on("removedfile", function(file) {
                if (addedFile == 1) {
                    $.ajax({
                        type: "GET",
                        url:  '/drop/?filename=' + filename,
                        success: function (data) {
                            addedFile = 0;
                            fileObj = null;
                            filename = "";
                            ocr_progress_status = 0;
                            estimated_time = 0;
                        },
                        error: function (x, e) {
                        }
                    })
                }
            });
        },

    };

    function displayError(html) {
        $('#upload-error-content')
            .empty()
            .html(html);
    };

    window.closeError = function() {
        $('#upload-error-content').empty();

        $('#upload-error').hide();

        $('#process-content-text').hide();

        $('#main-content-text').show();
    };

    myDropzone = new Dropzone("div#dropzone", options);

});

function dropUpload() {
    if(addedFile == 1){
        myDropzone.removeFile(fileObj);
        //$(".main .label").html(label_text);
        addedFile = 0;
        fileObj = null;
        filename = "";
        ocr_progress_status = 0;
        estimated_time = 0;
    }
}

function openYouTubeUrl() {
    var match, video

    var url = $('#youtube-url').val();

    if (url.length < 1 || !url) {
        $('#youtube-url-error')
            .text('')
            .hide();
        return;
    };

    if ((url.indexOf('youtube.com/watch?') == -1) && (url.indexOf('youtu.be') == -1)) {
        $('#youtube-url-error')
            .text('not a valid youtube video link')
            .show();
            return;
    };

    if ( (url.indexOf('youtu.be') != -1) && (url.indexOf('youtube') == -1) )  {
        video = url.split('/').slice(-1).pop(); 
    } else {
        match = RegExp('[?&]' + 'v=([^&]*)').exec(url);
        video = decodeURIComponent(match[1].replace(/\+/g, ' '));
    }

    if (!video || video.length < 5) {
        $('#youtube-url-error')
            .text('missing or incorrect video id in link')
            .show();
            return;
    };

    window.open('/video/' + video + '/', '_blank');

}
