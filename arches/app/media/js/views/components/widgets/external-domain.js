import ko from "knockout";
import ExternalDomainSelectViewModel from "viewmodels/external-domain-select";
import selectTemplate from "templates/views/components/widgets/select.htm";

const viewModel = function(params) {
    ExternalDomainSelectViewModel.apply(this, [params]);
    this.multiple = false;
};

export default ko.components.register("external-domain", {
    viewModel,
    template: selectTemplate,
});
