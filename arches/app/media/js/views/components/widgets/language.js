import ko from "knockout";
import LanguageSelectViewModel from "viewmodels/language-select";
import selectTemplate from "templates/views/components/widgets/select.htm";

const viewModel = function(params) {
    params.configKeys = ["defaultValue"];
    
    LanguageSelectViewModel.apply(this, [params]);
    const self = this;

    self.multiple = false;
    self.defaultValue = ko.observable(params.config.defaultValue || null);
};

export default ko.components.register("language-widget", {
    viewModel: viewModel,
    template: selectTemplate,
});