require([
    'jquery',
    'backbone',
    'arches',
    'models/concept',
    'views/rdm/concept-tree',
    'views/rdm/concept-report',
    'jquery-validate',
], function($, Backbone, arches, ConceptModel, ConceptTree, ConceptReport) {
    $(document).ready(function() {
        var concept = new ConceptModel({
                id: $('#selected-conceptid').val()
            }),
            conceptTree = new ConceptTree({
                el: $('#jqtree')[0],
                model: concept
            }),
            conceptReport = new ConceptReport({
                el: $('#concept_report')[0],
                model: concept
            });

        concept.on('change', function() {
            window.history.pushState({}, "conceptid", concept.get('id'));
        });

        conceptTree.on('conceptMoved', function (){
            conceptReport.render();
        });

        conceptReport.on({
            'valueSaved': function () {
                conceptTree.render();
            },
            'conceptDeleted': function () {
                conceptTree.render();
            },
            'conceptAdded': function () {
                conceptTree.render();
            }
        });
    });
});