import ko from "knockout";
import ExternalDomainSelectViewModel from "viewmodels/external-domain-select";
import selectTemplate from "templates/views/components/widgets/select.htm";

const viewModel = function(params) {
    params.configKeys = ["placeholder", "width", "uneditable", "defaultValue"];
    ExternalDomainSelectViewModel.apply(this, [params]);
    this.multiple = false;
};

export default ko.components.register("language-widget", {
    viewModel,
    template: selectTemplate,
});
