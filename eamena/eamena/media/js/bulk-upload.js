function updateRestype() {
    $('#restype-msg').text($('#resource-type-select').val());
    $('#resource-type-select').change( function() {
        $('#restype-msg').text($('#resource-type-select').val());
    });
    if (('#restype-msg').text() === "INFORMATION_RESOURCE.E73"){
        $('#folderupload').removeAttr('disabled')
    }
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
                $('#files-msg').css("color","red");
                $('#files-msg').text("Invalid file format rejected for upload.");
            } else {
                filepath = data.result.filepath;
                $('#files-msg').css("color","green");
                $('#files-msg').text(data.result.filename);
                $('#resource-type-select').removeAttr('disabled');
                $('#append-select').removeAttr('disabled');
                $('#validate-button').removeAttr('disabled');
            }
        },
        progressall: function (e, data) {
            var progress = parseInt(data.loaded / data.total * 100, 10);
            $('#progress .progress-bar').css(
                'width',
                progress + '%'
            );
        }
    }).prop('disabled', !$.support.fileInput)
        .parent().addClass($.support.fileInput ? undefined : 'disabled');
        
    $('#validate-button').click( function () {
        $('#validation-msg').css("color","orange");
        $('#validation-msg').text("Validating... this may take a while.");
        $('#validate-load-mask').show();
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
                $('#validate-load-mask').hide();
                var logEl = document.getElementById('upload-log-output');
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
                    $('#validation-msg').css("color","green");
                    $('#validation-msg').text("Validation complete. All tests passed.");
                    $('#import-msg').css("color","green");
                    $('#import-msg').text("Ready to load.");
                    archesFilepath = result.filepath;
                } else {
                    $('#validation-msg').css("color","red");
                    $('#validation-msg').text("Validation complete. Some tests failed. Fix the errors locally and re-upload the file.");
                }
            }
        });
    });
    $('#load-data-button').click( function () {
        $('#import-msg').css("color","orange");
        $('#import-msg').text("Importing data... this may take a while.");
        $('#full-load-mask').show();
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
            success: function(result) {
                if (result.errors) {
                    console.log("python errors:");
                    console.log(result.errors);
                }
                window.location.href = $("#bulk-url").attr("data-url");
            }
        });
    });

    $('#folderupload').fileupload({
        beforeSend: function(request) {
            request.setRequestHeader("X-CSRFToken",csrftoken);
        },
        dataType: 'json',
        done: function (e, data) {
            console.log(data)
            if (!data.result.filevalid) {
                // note that invalid file types will not have been uploaded
                $('#folder-msg').css("color","red");
                $('#folder-msg').text("Invalid file format rejected for upload.");
            } else {
                filepath = data.result.filepath;
                $('#folder-msg').css("color","green");
                $('#folder-msg').text(data.result.filename);
            }
        }
    }).prop('disabled', !$.support.fileInput)
        .parent().addClass($.support.fileInput ? undefined : 'disabled');

    updateRestype();
});

