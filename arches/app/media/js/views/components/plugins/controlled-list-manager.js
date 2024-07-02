import ko from 'knockout';
import ControlledListManager from '@/plugins/ControlledListManager.vue';
import createVueApp from 'utils/create-vue-application';
import ControlledListManagerTemplate from 'templates/views/components/plugins/controlled-list-manager.htm';


ko.components.register('controlled-list-manager', {
    viewModel: function() {
        createVueApp(ControlledListManager).then((vueApp) => {
            vueApp.mount('#controlled-list-manager-mounting-point');
        })
    },
    template: ControlledListManagerTemplate,
});
