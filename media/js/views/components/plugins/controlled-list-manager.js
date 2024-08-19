import ko from 'knockout';

import { routes } from '@/arches_references/routes.ts';
import ControlledListManager from '@/arches_references/plugins/ControlledListManager.vue';
import createVueApplication from 'utils/create-vue-application';
import ControlledListManagerTemplate from 'templates/views/components/plugins/controlled-list-manager.htm';

import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
  history: createWebHistory(),
  routes,
});

ko.components.register('controlled-list-manager', {
    viewModel: function() {
        createVueApplication(ControlledListManager).then((vueApp) => {
            vueApp.use(router);
            vueApp.mount('#controlled-list-manager-mounting-point');
        });
    },
    template: ControlledListManagerTemplate,
});
