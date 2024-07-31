import ko from 'knockout';

import ControlledListManager from '@/arches_references/plugins/ControlledListManager.vue';
import ControlledListsMain from '@/arches_references/components/ControlledListsMain.vue';
import createVueApplication from 'utils/create-vue-application';
import ControlledListManagerTemplate from 'templates/views/components/plugins/controlled-list-manager.htm';

import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  { path: '/plugins/controlled-list-manager', name: 'splash', component: ControlledListsMain },
  { path: '/plugins/controlled-list-manager/list/:id', name: 'list', component: ControlledListsMain },
  { path: '/plugins/controlled-list-manager/item/:id', name: 'item', component: ControlledListsMain },
];

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
