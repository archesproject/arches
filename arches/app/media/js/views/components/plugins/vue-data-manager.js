import ko from 'knockout';
import VueDataManagerApplication from '@/components/vue-data-manager/vue-data-manager.vue';
import createVueApplication from 'utils/create-vue-application';
import VueDataManagerAppTemplate from 'templates/views/components/plugins/vue-data-manager.htm';

ko.components.register('vue-data-manager', {
    viewModel: function() {
        createVueApplication(VueDataManagerApplication).then(vueApp => {
            vueApp.mount('#vue-data-manager-mounting-point');
        });
    },
    template: VueDataManagerAppTemplate,
});