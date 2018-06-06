function updateRestype() {
    $('#restype-msg').text($('#resource-type-select').val());
    $('#resource-type-select').change( function() {
        $('#restype-msg').text($('#resource-type-select').val());
    });
};

function displayResults(result,testName,logEl) {
    var passColor = 'green';
    var failColor = 'red';
    var pass = true;
    if (result.passed) {
        t = testName+": PASS";
        logEl.insertAdjacentHTML('beforeend',
            '<p class="log-line" style="color:'+passColor+'">'+t+'</p>'
        );
    } else {
        pass = false;
        t = testName+": FAIL";
        logEl.insertAdjacentHTML('beforeend',
            '<p class="log-line" style="color:'+failColor+'">'+t+'</p>'
        );
        $.each(result.errors, function (index, line) {
            logEl.insertAdjacentHTML('beforeend',
                '<p class="log-line" style="color:'+failColor+'">'+line+'</p>'
            );
        });
    }
    return pass;
}

$( document ).ready(function() {
    
    var filepath = '';
    var archesFilepath = '';

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
                $('#resource-type-select').removeAttr('disabled');
                $('#append-select').removeAttr('disabled');
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
                'restype':$('#resource-type-select').val(),
                'append':$('#append-select').val(),
            },
            done: function (result) {
            },
            success: function(result) {
                $('.form-load-mask').hide();
                var logEl = document.getElementById('upload-log-output');
                console.log(result);
                var allPassed = true;
                
                
                var testList = new Array(
                    'validate_headers',
                    'validate_rows_and_values',
                    'validate_dates',
                    'validate_geometries',
                    'validate_concepts'
                );
                
                $.each(testList, function (index, test) {
                    var pass = displayResults(result[test],test,logEl);
                    if (!pass) {
                        allPassed = false;
                        return false; // this line breaks the reporting early
                    };
                });
                if (allPassed) {
                    $('#load-data-button').removeAttr('disabled');
                    $('#validation-msg').text("Validation complete. All tests passed.");
                    archesFilepath = result.filepath;
                } else {
                    $('#validation-msg').text("Validation complete. Some tests failed.");
                }
            }
        });
    });
    $('#load-data-button').click( function () {
        $('#import-msg').text("Importing data... this may take a few minutes.");
        $.ajax({
            beforeSend: function(request) {
                request.setRequestHeader("X-CSRFToken",csrftoken);
            },
            url: '/bulk-upload/import',
            type: 'post',
            data: {
                'filepath':archesFilepath,
                'append':$('#append-select').val(),
            },
            done: function (result) {
            },
            success: function(result) {
                
                console.log(result);
                
            }
        });
    });
    
    updateRestype();

});

