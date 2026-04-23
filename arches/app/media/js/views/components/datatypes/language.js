import ko from 'knockout';
import { ExternalDomainConfigViewModel } from 'views/components/datatypes/external-domain';
import languageDatatypeTemplate from 'templates/views/components/datatypes/language.htm';

const name = 'language-datatype-config';

ko.components.register(name, {
    viewModel: ExternalDomainConfigViewModel,
    template: languageDatatypeTemplate,
});

export default name;
