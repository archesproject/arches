function updateRestype() {
    $('#restype-msg').text($('#resource-type-select').val());
    $('#resource-type-select').change( function() {
        $('#restype-msg').text($('#resource-type-select').val());
    });
};

// sleep function just for testing
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function displayResults(result,testName) {
    var logEl = document.getElementById('upload-log-output');
    var passColor = 'green';
    var failColor = 'red';
    if (result.success) {
        t = testName+": PASS";
        logEl.insertAdjacentHTML('beforeend',
            '<p class="log-line" style="color:'+passColor+'">'+t+'</p>'
        );
    } else {
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
    return
}

function setValPostData(valType,filePath) {
    data = {
        'validationtype':valType,
        'filepath':filePath,
        'restype':$('#resource-type-select').val(),
        'append':$('#append-select').val(),
    }
    return data
}

function postValidation(passed,valType,filePath) {
    if (!passed) {return passed}
    
    xhr = $.ajax({
        beforeSend: function(request) {
            request.setRequestHeader("X-CSRFToken",csrftoken);
        },
        url: '/bulk-upload/validate',
        type: 'post',
        data: setValPostData(valType,filePath),
        done: function (result) {
        },
        success: function(result) {
            
            
            var logEl = document.getElementById('upload-log-output');
            displayResults(result,valType,logEl)
            if (!result.success) {passed = false};
            return passed
        }
    });
}

$( document ).ready(function() {
    
    var filepath = '';
    var archesFilepath = '';
    var formdata = new FormData();
    var xhr = null;

    'use strict';
    var csrftoken = $("[name=csrfmiddlewaretoken]").val();
    $('#excelfileupload').fileupload({
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
                filePath = data.result.filepath;
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
        $('#cancel-button').removeAttr('disabled');
        $('.log-line').remove();
        
        var testList = new Array(
            'headers',
            'rows_and_values',
            'dates',
            // 'geometries',
            // 'concepts',
            // 'files'
        );
        var testCt = testList.length
        var passed = true;
        function headers () {
            test = 'headers';
            return $.ajax({
                beforeSend: function(request) {
                    request.setRequestHeader("X-CSRFToken",csrftoken);
                },
                url: '/bulk-upload/validate',
                type: 'post',
                data: setValPostData(test,filePath),
                success: function(result) {
                    
                    displayResults(result,test)
                    if (!result.success) {passed = false};
                }
            });
        }
        function rows_and_values(data, textStatus, jqXHR) {
            if (!data.success) {return false}
            test = 'rows_and_values';
            return $.ajax({
                beforeSend: function(request) {
                    request.setRequestHeader("X-CSRFToken",csrftoken);
                },
                url: '/bulk-upload/validate',
                type: 'post',
                data: setValPostData(test,filePath),
                success: function(result) {
                    displayResults(result,test)
                    if (!result.success) {passed = false};
                }
            });
        }
        
        function dates(data, textStatus, jqXHR) {
            if (!data.success) {return false}
            test = 'dates';
            return $.ajax({
                beforeSend: function(request) {
                    request.setRequestHeader("X-CSRFToken",csrftoken);
                },
                url: '/bulk-upload/validate',
                type: 'post',
                data: setValPostData(test,filePath),
                success: function(result) {
                    displayResults(result,test)
                    if (!result.success) {passed = false} else {archesFilepath = result.filepath;};
                }
            });
        }
        
        function geometries(data, textStatus, jqXHR) {
            if (!data.success) {return false}
            test = 'geometries';
            return $.ajax({
                beforeSend: function(request) {
                    request.setRequestHeader("X-CSRFToken",csrftoken);
                },
                url: '/bulk-upload/validate',
                type: 'post',
                data: setValPostData(test,filePath),
                success: function(result) {
                    displayResults(result,test)
                    if (!result.success) {passed = false} else {archesFilepath = result.filepath;};
                }
            });
        }
        
        function concepts(data, textStatus, jqXHR) {
            if (!data.success) {return false}
            test = 'concepts';
            return $.ajax({
                beforeSend: function(request) {
                    request.setRequestHeader("X-CSRFToken",csrftoken);
                },
                url: '/bulk-upload/validate',
                type: 'post',
                data: setValPostData(test,filePath),
                success: function(result) {
                    displayResults(result,test)
                    if (!result.success) {passed = false} else {archesFilepath = result.filepath;};
                }
            });
        }
        
        function files(data, textStatus, jqXHR) {
            if (!data.success) {return false}
            test = 'files';
            return $.ajax({
                beforeSend: function(request) {
                    request.setRequestHeader("X-CSRFToken",csrftoken);
                },
                url: '/bulk-upload/validate',
                type: 'post',
                data: setValPostData(test,filePath),
                success: function(result) {
                    displayResults(result,test)
                    if (!result.success) {passed = false} else {archesFilepath = result.filepath;};
                    if ($('#resource-type-select').val() === "INFORMATION_RESOURCE.E73"){
                        if (result.hasfiles) {
                            $('#folder-upload-div').removeAttr('hidden');
                        }
                    }
                }
            });
        }
        
        function writefile(data, textStatus, jqXHR) {
            if (!data.success) {return false}
            test = 'write_arches_file';
            return $.ajax({
                beforeSend: function(request) {
                    request.setRequestHeader("X-CSRFToken",csrftoken);
                },
                url: '/bulk-upload/validate',
                type: 'post',
                data: setValPostData(test,filePath),
                success: function(result) {
                    displayResults(result,test)
                    if (!result.success) {passed = false} else {archesFilepath = result.filepath;};
                }
            });
        }
        
        function validateMsgs (){
            if (passed) {
                $('#validate-load-mask').hide();
                $('#load-data-button').removeAttr('disabled');
                $('#validation-msg').css("color","green");
                $('#validation-msg').text("Validation complete. All tests passed.");
                $('#import-msg').css("color","green");
                $('#import-msg').text("Ready to load.");
                formdata.append('archesfile', archesFilepath)
                
            } else {
                $('#validate-load-mask').hide();
                $('#validation-msg').css("color","red");
                $('#validation-msg').text("Validation failed. Fix the errors locally and re-upload the file.");
            }
        }
        
        // chain all individual validation ajax requests together to simulate asynchronous behavior
        headers().then(rows_and_values).then(dates).then(geometries).then(concepts).then(files).then(writefile).then(validateMsgs);

    });

    $('#cancel-button').click( function () {
        xhr.abort();
        $('#cancel-button').disabled = true;
        $('#validate-load-mask').hide();
        $('#validation-msg').css("color","red");
        $('#validation-msg').text("Validation canceled.");
        $('.log-line').remove();
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
                formdata.append('resdict', result.load_id)
                if ($('#folder-upload-div').is(":visible")) {
                    $('#full-load-mask').hide();
                    $('#import-msg').css("color", "green");
                    $('#import-msg').text("Resources imported");
                }else {
                    window.location.href = $("#bulk-url").attr("data-url");
                }
            }
        });
    });
    $('#folderupload').change( function () {
        $('#folder-msg').css("color","orange");
        $('#folder-msg').text("Uploading files... this may take a while.");
    });   
    $('#folderupload').fileupload({
            beforeSend: function(request) {
                request.setRequestHeader("X-CSRFToken",csrftoken);
            },
            dataType: 'json',
            formData: formdata,
            done: function (e, data) {
                if (!data.result.foldervalid) {
                    // note that resources will have been uploaded with missing images
                    $('#folder-msg').css("color","red");
                    $('#folder-msg').text("Failed to identify matching resource.");
                } else {
                    $('#folder-msg').css("color","green");
                    $('#folder-msg').text("Upload successful - click finished!");
                    $('#folder-upload-btn').removeAttr('disabled');
                }
            },
        }).prop('disabled', !$.support.fileInput)
            .parent().addClass($.support.fileInput ? undefined : 'disabled');


    $('#folder-upload-btn').click(function () {
        window.location.href = $("#bulk-url").attr("data-url");
    });


    updateRestype();
});

