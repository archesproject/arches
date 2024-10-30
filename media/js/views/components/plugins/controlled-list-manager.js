import ko from 'knockout';

import { definePreset } from '@primevue/themes';
import { ArchesPreset, DEFAULT_THEME } from '@/arches/themes/default.ts';
import { routes } from '@/arches_references/routes.ts';
import ControlledListManager from '@/arches_references/plugins/ControlledListManager.vue';
import createVueApplication from 'utils/create-vue-application';
import ControlledListManagerTemplate from 'templates/views/components/plugins/controlled-list-manager.htm';

import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
  history: createWebHistory(),
  routes,
});

const ControlledListsPreset = definePreset(ArchesPreset, {
    semantic: {
        iconSize: 'small',
    },
    components: {
        button: {
            root: {
                label: {
                    fontWeight: 600,
                },
            },
        },
    },
});

const ControlledListsTheme = {
    theme: {
        ...DEFAULT_THEME,
        preset: ControlledListsPreset,
    },
};

ko.components.register('controlled-list-manager', {
    viewModel: function() {
        createVueApplication(ControlledListManager, ControlledListsTheme).then((vueApp) => {
            vueApp.use(router);
            vueApp.mount('#controlled-list-manager-mounting-point');
        });
    },
    template: ControlledListManagerTemplate,
});
