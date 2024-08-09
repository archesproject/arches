import ko from 'knockout';

import ControlledListManager from '@/arches_references/plugins/ControlledListManager.vue';
import createVueApplication from 'utils/create-vue-application';
import ControlledListManagerTemplate from 'templates/views/components/plugins/controlled-list-manager.htm';

ko.components.register('controlled-list-manager', {
    viewModel: function() {
        createVueApplication(ControlledListManager).then((vueApp) => {
            vueApp.mount('#controlled-list-manager-mounting-point');
        });
    },
    template: ControlledListManagerTemplate,
});
