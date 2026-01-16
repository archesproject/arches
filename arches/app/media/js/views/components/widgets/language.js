import ko from "knockout";
import arches from "arches";
import WidgetViewModel from "viewmodels/widget";
import selectTemplate from "templates/views/components/widgets/select.htm";

const viewModel = function(params) {
    params.configKeys = ["defaultValue", "placeholder", "width", "uneditable"];
    
    WidgetViewModel.apply(this, [params]);
    const self = this;

    self.options = ko.observableArray();
    self.multiple = false; // TODO: allow multiselect?

    self.displayValue = ko.computed(() => {
        const selectedOption = self.options().find(
            (option) => option.id === self.value()
        );
        return selectedOption ? selectedOption.text : "";
    });
    
    const init = async() => {
        const response = await fetch(arches.urls.languages);
        const data = await response.json();
        const languages = data?.languages.map(lang => {
            return {id: lang.code, text: lang.name};
        });
        self.options(languages);
    }

    init();
};

export default ko.components.register("language-widget", {
    viewModel: viewModel,
    template: selectTemplate,
});