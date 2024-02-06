import ko from 'knockout';
import ToastService from 'primevue/toastservice';
import Tooltip from 'primevue/tooltip';
import ControlledListManager from '@/plugins/ControlledListManager.vue';
import createVueApplication from 'utils/create-vue-application';
import ControlledListManagerTemplate from 'templates/views/components/plugins/controlled-list-manager.htm';


ko.components.register('controlled-list-manager', {
    viewModel: function() {
        createVueApplication(ControlledListManager).then((vueApp) => {
            vueApp.use(ToastService);  // TODO: move to createVueApplication
            vueApp.directive('tooltip', Tooltip);
            vueApp.mount('#controlled-list-manager-mounting-point');
        })
    },
    template: ControlledListManagerTemplate,
});
