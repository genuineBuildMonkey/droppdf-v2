(function() {

    /* 50 minute max time */
    var max = 600
    var c = 0

    var stop_time;
    var start_time = new Date();

    function _show_complete() {
        clearInterval(check_interval);

        stop_time = new Date();

        var time_to_process = ((stop_time - start_time) / 1000).toFixed(2)

        $('#in-progress').hide();
        $('#download-info').show();

        $('#processing-time').text(time_to_process);

        $('#docdrop-link').attr('href', '/pdf/' + FILE_INFO.processed_filename)

        $('#file-download-link').attr('href', FILE_INFO.download_url)
    };


    var check_interval = setInterval(function() {
        $.post('/ocr_pdf_complete', {filename: FILE_INFO.new_filename})
        .done(function(result) {
            _show_complete();
            return;

        })
        .fail(function(e) {
        });

        c += 1

        if (c > max) {
            clearInterval(check_interval);
            $('#in-progress').hide();
            $('#download-info').hide();
            $('#upload-error').show();

        };
    }, 5000);

    $(document).ready(function() {
        $('#time-start').text(start_time.toLocaleTimeString());

        //var url = window.location.origin;
        //url += '/static/drop-pdf/' + FILE_INFO.new_filename;

        //$('#download-link')
            //.attr('href', url)
            //.text(url);

        $('#docdrop-link')
            .attr('href', '/pdf/' + FILE_INFO.new_filename)
            .text(FILE_INFO.new_filename);

        /* ocr previously performed */
        if (FILE_INFO.already_exists) {
            clearInterval(check_interval);
            _show_complete();
        }

        else if (FILE_INFO.processing_error) {
            clearInterval(check_interval);

            $('#in-progress').hide();
            $('#download-info').hide();
            $('#upload-error')
                .text(FILE_INFO.processing_error)
                .show();
        }
    });

}());
