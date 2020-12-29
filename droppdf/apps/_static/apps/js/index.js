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

    //store label text so we can put it back
    //after upload without typing all that again
    var label_text = $('.label').first().html();

    $( "#progressbar" ).progressbar({
        value: 0
    });
    $( "#progressbar" ).hide();

    var options = {
        url: "/upload/",

        paramName: "file", // The name that will be used to transfer the file
        clickable: false,
        accept: function(file, done) {
            fileObj = file;
            $(".main .label").html("<a href='javascript:void(0)' onclick='dropUpload()'>Uploading...</a>")
            done();
          },
        init: function() {
            this.on("addedfile", function(file) {
                var extention = file.name.split(".");
                extention = extention[extention.length-1];
            
                if (extention == 'pdf' || extention == 'docx' || extention == 'xlsx' || extention == 'doc' || extention == 'xls'|| extention == 'csv' || extention == 'epub'){
                    type = extention
                    if (addedFile == 0) {
                        addedFile = 1;
                    }
                    else {
                        this.removeFile(file);
                    }
                }
                else{
                    setTimeout(function() { 
                        alert('Upload Error: Document format not recognized.');
                        $(".main .label").html(label_text);
                        }, 700);
                    this.removeFile(file);
                }

            });

        this.on("success", function(file, filename_server) {
            if(type == 'pdf' || type == 'docx' || type == 'doc')
            {
                filename = filename_server;
                check_list = filename.split("-");
                check = check_list[0];
                page_num = check_list[1];
                temp = [];

                for(i=2; i<check_list.length; i++)
                    temp.push(check_list[i]);

                temp = temp.join("-");

                // start to ocr pdf
                if(check == "false")
                {
                    estimated_time = Math.round( page_num * 8 );
                
                    label = '<div style="font-size:18px">' + page_num.toString() + ' pages to OCR, estimate ' + estimated_time.toString() + ' seconds to complete</div>';
                    $(".main .label").html("OCRing..." + label);

                    $( "#progressbar" ).show();
                    ocr_progress = setInterval(function(){ 
                                        if(ocr_progress_status <= estimated_time * 1000)
                                        {
                                            remain_time = Math.round((estimated_time * 1000 - ocr_progress_status) / 1000)
                                            label = '<div style="font-size:18px">' + page_num.toString() + ' pages to OCR, estimate ' + remain_time.toString() + ' seconds to complete</div>';
                                            $(".main .label").html("OCRing..." + label);
                                            ocr_progress_status += estimated_time * 10;
                                            $( "#progressbar" ).progressbar({
                                                value: ocr_progress_status / (estimated_time * 10)
                                            });
                                        }
                                        else{
                                            clearInterval(ocr_progress);
                                        }
                                    }, estimated_time * 10);

                    $.ajax({
                        type: "GET",
                        url:  '/ocr/?filename=' + temp,
                        success: function (data) {
                            clearInterval(ocr_progress);
                            ocr_progress_status = 0;
                            estimated_time = 0;
                            $( "#progressbar" ).hide();
                            $(".main .label").html("<a href='javascript:void(0)' onclick='dropUpload()'>Drop to upload</a>");
                            window.location.href = 'pdf/' + data + '/';
                        },
                        error: function (x, e) {
                        }
                    })
                }
                else if(check == 'true')
                {
                
                    $(".main .label").html("<a href='javascript:void(0)' onclick='dropUpload()'>Drop to upload</a>");
                    window.location.href = 'pdf/' + temp + '/';
                }
                else
                {
                    alert("This file is not a pdf or corrupted.");
                    $(".main .label").html("<a href='javascript:void(0)' onclick='dropUpload()'>Drop to upload</a>")
                }
            }
            else if (type == "epub") {
                $(".main .label").html("<a href='javascript:void(0)' onclick='dropUpload()'>Drop to upload</a>");
                window.location.href = 'epub/' + filename_server + '/';
            }
            else
            {
                $(".main .label").html("<a href='javascript:void(0)' onclick='dropUpload()'>Drop to upload</a>");
                //var ip = location.host;
                //window.location.href = "https://via.hypothes.is/http://datapipes.okfnlabs.org/csv/html/?url= http://" + ip + "/static/" + "drop-pdf/" + filename_server;
                
                window.location.href = 'csv/' + filename_server + '/';
            }

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

    myDropzone = new Dropzone("div#myId", options);
});

function dropUpload() {
    if(addedFile == 1){
        myDropzone.removeFile(fileObj);
        $(".main .label").html(label_text);
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
