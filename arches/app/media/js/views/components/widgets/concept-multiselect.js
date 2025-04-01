import ko from 'knockout';
import ConceptSelectViewModel from 'viewmodels/concept-select';
import conceptMultiselectTemplate from 'templates/views/components/widgets/concept-select.htm';
import 'bindings/select2-query';


const viewModel = function(params) {
    params.multiple = true;
    params.configKeys = ['defaultValue'];

        
    ConceptSelectViewModel.apply(this, [params]);

    var defaultValue = ko.unwrap(this.defaultValue);
    var self = this;

    if (self.configForm){
        self.select2Config.value = self.defaultValue;
    }
};

export default ko.components.register('concept-multiselect-widget', {
    viewModel: viewModel,
    template: conceptMultiselectTemplate,
});
