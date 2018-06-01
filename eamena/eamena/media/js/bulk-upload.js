$( document ).ready(function() {
    var filepath = '';
    'use strict';
    var csrftoken = $("[name=csrfmiddlewaretoken]").val();
    $('#fileupload').fileupload({
        beforeSend: function(request) {
            request.setRequestHeader("X-CSRFToken",csrftoken);
        },
        dataType: 'json',
        done: function (e, data) {
            if (!data.result.filevalid) {
                // note that invalid file types will not have been uploaded
                $('#files-msg').text("Invalid file format rejected for upload.");
            } else {
                filepath = data.result.filepath;
                $('#files-msg').text(data.result.filename);
                $('.resource-type-select').removeAttr('disabled');
                $('#validate-button').removeAttr('disabled');
            }
        },
        progressall: function (e, data) {
            var progress = parseInt(data.loaded / data.total * 100, 10);
            console.log(progress);
            $('#progress .progress-bar').css(
                'width',
                progress + '%'
            );
        }
    }).prop('disabled', !$.support.fileInput)
        .parent().addClass($.support.fileInput ? undefined : 'disabled');
        
    $('#validate-button').click( function () {
        console.log("validating...");
        $('#validation-msg').text("Validating...");
        $('.form-load-mask').show();
        $('.log-line').remove();
        $.ajax({
            beforeSend: function(request) {
                request.setRequestHeader("X-CSRFToken",csrftoken);
            },
            url: '/bulk-upload/validate',
            type: 'post',
            data: {
                'filepath':filepath,
                'restype':$('.resource-type-select').val(),
            },
            done: function (result) {
            },
            success: function(result) {
                $('.form-load-mask').hide();
                $('#validation-msg').text("Validation complete.");
                var logEl = document.getElementById('upload-log-output');
                $.each(result.msg, function (index, line) {
                    var textColor = 'green';
                    if (line.slice(0,5)=='ERROR') { textColor = 'red' }
                    logEl.insertAdjacentHTML('beforeend', '<p class="log-line" style="color:'+textColor+'">'+line+'</p>');
                });
            }
        });
    });
    $('#load-data-button').click( function () {
        console.log("Loading data...");
        // nothing here yet, but it will be another ajax call
    });
    
    updateRestype();
});

var updateRestype = new function() {
    $('#restype-msg').text($('.resource-type-select').val());
    $('.resource-type-select').change( function() {
        $('#restype-msg').text($('.resource-type-select').val());
    });
};
