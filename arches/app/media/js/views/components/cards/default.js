import ko from 'knockout';
import CardComponentViewModel from 'viewmodels/card-component';
import defaultCardTemplate from 'templates/views/components/cards/default.htm';

export default ko.components.register('default-card', {
    viewModel: CardComponentViewModel,
    template: defaultCardTemplate,
});
