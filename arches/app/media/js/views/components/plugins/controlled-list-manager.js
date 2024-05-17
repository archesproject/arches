import ko from 'knockout';
import ControlledListManager from '@/arches/plugins/ControlledListManager.vue';
import createVueApp from 'utils/create-vue-application';
import ControlledListManagerTemplate from 'templates/views/components/plugins/controlled-list-manager.htm';

import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  { path: '/plugins/controlled-list-manager', name: 'splash', component: ControlledListManager },
  { path: '/plugins/controlled-list-manager/list/:id', name: 'list', component: ControlledListManager },
  { path: '/plugins/controlled-list-manager/item/:id', name: 'item', component: ControlledListManager },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

ko.components.register('controlled-list-manager', {
    viewModel: function() {
        createVueApp(ControlledListManager).then((vueApp) => {
            vueApp.use(router);
            vueApp.mount('#controlled-list-manager-mounting-point');
        });
    },
    template: ControlledListManagerTemplate,
});
