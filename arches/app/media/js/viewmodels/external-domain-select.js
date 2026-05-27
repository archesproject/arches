import ko from "knockout";
import arches from "arches";
import WidgetViewModel from "viewmodels/widget";

const OPTIONS_CACHE = {};

const ExternalDomainSelectViewModel = function(params) {
    params.configKeys = params.configKeys || ["placeholder", "width", "uneditable", "defaultValue"];
    WidgetViewModel.apply(this, [params]);
    const self = this;

    self.options = ko.observableArray();

    self.displayValue = ko.computed(() => {
        const selectedOption = self.options().find(
            (option) => String(option.id) === String(self.value())
        );
        return selectedOption ? selectedOption.text : "";
    });

    const datatype = self.node && ko.unwrap(self.node.datatype);
    if (datatype) {
        if (OPTIONS_CACHE[datatype]) {
            self.options(OPTIONS_CACHE[datatype]);
        } else {
            fetch(arches.urls.api_external_domain_options(datatype))
                .then((response) => response.json())
                .then((data) => {
                    OPTIONS_CACHE[datatype] = data.options;
                    self.options(data.options);
                })
                .catch((err) => console.error(`Error fetching options for "${datatype}":`, err));
        }
    }
};

export default ExternalDomainSelectViewModel;
