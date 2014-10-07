require([
    'jquery',
    'arches',
    'models/concept',
    'models/value',
    'views/concept-tree',
    'views/value-editor',
    'jquery-validate',
], function($, arches, ConceptModel, ValueModel, ConceptTree, ValueEditor) {
    $(document).ready(function() {
        var conceptModel = new ConceptModel(),
            conceptTree = new ConceptTree({
                el: $('#jqtree')[0],
                model: conceptModel
            }),
            conceptEditor = $('#conceptmodal'),
            loadConceptReport = function(conceptid) {
                $('#concept_report_loading').removeClass('hidden');
                $('#concept_report').addClass('hidden');
                $.ajax({
                    url: '../Concepts/' + conceptid + '?f=html',
                    success: function(response) {
                        $('#concept_report_loading').addClass('hidden');
                        $('#concept_report').removeClass('hidden');
                        $('#concept_report').html(response);
                    }
                });
            },
            addConcept = function(data, successCallback, errorCallback) {
                $.ajax({
                    type: "POST",
                    url: arches.urls.concept,
                    data: JSON.stringify(data),
                    success: successCallback,
                    error: errorCallback
                });
            },
            deleteConcept = function(data, successCallback, errorCallback) {
                $.ajax({
                    type: "DELETE",
                    url: arches.urls.concept + data,
                    success: successCallback,
                    error: errorCallback
                });
            },
            reloadReport = function() {
                loadConceptReport(conceptModel.get('id'));
            },
            reloadConcept = function() {
                conceptTree.render();
            };

        conceptModel.on('change', function () {
            window.history.pushState({}, "conceptid", conceptModel.get('id'));
            loadConceptReport(conceptModel.get('id'));
        });

        conceptTree.on('conceptMoved', function (conceptid) {
            if (conceptModel.get('id') === conceptid) {
                reloadReport();
            }
        });

        // ADD CHILD CONCEPT EDITOR 
        conceptEditor.validate({
            ignore: null, // required so that the select2 dropdowns will be visible to the validate plugin
            rules: {
                // element_name: value
                label: "required",
                language_dd: "required"
            },
            submitHandler: function(form) {
                var data = {
                    label: $(form).find("[name=label]").val(),
                    note: $(form).find("[name=note]").val(),
                    language: $(form).find("[name=language_dd]").select2('val'),
                    parentconceptid: conceptModel.get('id')
                };

                addConcept(data, function(data) {
                    conceptEditor.modal('hide');
                    reloadConcept();
                }, null);
            }
        });

        // CLICK LISTENER 
        $(document).on('click', '#concept_report a', function() {
            var data = $(this).data();
            if (data.action === 'delete' || data.action === 'delete_concept') {
                $('#confirm_delete_modal .modal-title').text($(this).attr('title'));
                $('#confirm_delete_modal .modal-body').text(data.message);
                $('#confirm_delete_modal').modal('show');
                $('#confirm_delete_yes').data('id', data.id);
                $('#confirm_delete_yes').data('action', data.action);
            }

            if (data.action === 'viewconcept') {
                conceptModel.set({id: data.conceptid });
            }
        });
        $(document).on('click', 'a.edit-value', function (e) {
            var data = $.extend({ conceptid: conceptModel.get('id') }, $(e.target).data()),
                model = new ValueModel(data),
                editor = new ValueEditor({
                    el: $(data.target)[0],
                    model: model
                });

            editor.on('submit', function () {
                model.save(reloadConcept);
            });
        });
        $('#confirm_delete_yes').on('click', function() {
            var data = $(this).data();
            if (data.action === 'delete') {
                var model = new ValueModel(data);
                model.delete(function () {
                    $('#confirm_delete_modal').modal('hide');
                    reloadReport();
                });
            }
            if (data.action === 'delete_concept') {
                deleteConcept(data.id, function(data) {
                    $('#confirm_delete_modal').modal('hide');
                    reloadConcept();
                }, null);
            }
        });
        $('#add_child_concept').on('click', function() {
            addConcept();
        });
    });
});