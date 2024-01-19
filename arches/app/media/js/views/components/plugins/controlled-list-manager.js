import ko from 'knockout';
import { createApp } from 'vue';
import PrimeVue from 'primevue/config';
import ControlledListManagerApp from '@/App.vue';
import ControlledListManager from 'templates/views/components/plugins/controlled-list-manager.htm';

import 'primevue/resources/themes/bootstrap4-light-blue/theme.css';

ko.components.register('controlled-list-manager', {
    viewModel: function() {
        const app = createApp(ControlledListManagerApp);
        app.use(PrimeVue);
        app.mount('#controlled-list-mounting-point');
    },
    template: ControlledListManager,
});
