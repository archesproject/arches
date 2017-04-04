define(['arches', 'knockout'], function (arches, ko) {
    var name = 'concept-datatype-config';
    ko.components.register(name, {
        viewModel: function(params) {
            this.topConcept = params.config.rdmCollection;
            this.conceptCollections = arches.conceptCollections;
            this.conceptCollections.unshift({
              'label': null,
              'id': null
            })
        },
        template: { require: 'text!datatype-config-templates/concept' }
    });
    return name;
});
