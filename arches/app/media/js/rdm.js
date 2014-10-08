require([
    'jquery',
    'backbone',
    'arches',
    'models/concept',
    'views/concept-tree',
    'views/concept-report',
    'jquery-validate',
], function($, Backbone, arches, ConceptModel, ConceptTree, ConceptReport) {
    $(document).ready(function() {
        var activeConcept = new ConceptModel(),
            conceptTree = new ConceptTree({
                el: $('#jqtree')[0],
                model: activeConcept
            }),
            conceptReport = new ConceptReport({
                el: $('#concept_report')[0],
                model: activeConcept
            });

        activeConcept.on('change', function() {
            window.history.pushState({}, "conceptid", activeConcept.get('id'));
        });

        conceptTree.on('conceptMoved', function(conceptid) {
            if (activeConcept.get('id') === conceptid) {
                conceptReport.render();
            }
        });

        conceptReport.on({
            'valueSaved': conceptTree.render,
            'conceptDeleted': conceptTree.render
        });

        // ADD CHILD CONCEPT EDITOR 
        $('#conceptmodal').validate({
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
                        parentconceptid: activeConcept.get('id')
                    },
                    concept = new ConceptModel(data);
                concept.save(function(data) {
                    $('#conceptmodal').modal('hide');
                    conceptTree.render();
                });
            }
        });
    });
});