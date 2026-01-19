import ko from "knockout";
import arches from "arches";
import WidgetViewModel from "viewmodels/widget";
import selectTemplate from "templates/views/components/widgets/select.htm";

let LANGUAGE_LOOKUP = {};
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

    async function fetchLanguages() {
        const languages = await fetch(arches.urls.languages)
            .then((response) => response.json())
            .then((data) => data.languages);
        return languages;
    }

    async function updateLanguageLookups() {
        const languageCodes = Object.keys(LANGUAGE_LOOKUP);
        if (languageCodes.length === 0) {
            const languages = await fetchLanguages();
            const options = languages.map((lang) => {
                LANGUAGE_LOOKUP[lang.code] = lang.name;
                return { id: lang.code, text: lang.name };
            });
            self.options(options);
        }
        else if (languageCodes.length > 0 && self.options().length <=0) {
            self.options(
                Object.entries(LANGUAGE_LOOKUP).map(
                    ([code, name]) => (
                        { id: code, text: name }
                    )
                )
            );
        }
    }
    
    const init = async() => {
        await updateLanguageLookups();
    }

    init();
};

export default ko.components.register("language-widget", {
    viewModel: viewModel,
    template: selectTemplate,
});