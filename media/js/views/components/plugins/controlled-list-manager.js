import ko from 'knockout';

import { definePreset } from '@primeuix/themes';
import { ArchesPreset, DEFAULT_THEME } from '@/arches/themes/default.ts';
import { routes } from '@/arches_controlled_lists/routes.ts';
import ControlledListManager from '@/arches_controlled_lists/plugins/ControlledListManager.vue';
import createVueApplication from 'utils/create-vue-application';
import ControlledListManagerTemplate from 'templates/views/components/plugins/controlled-list-manager.htm';

import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
  history: createWebHistory(),
  routes,
});

const ControlledListsPreset = definePreset(ArchesPreset, {
    semantic: {
        iconSize: '1.2rem',
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
        ...DEFAULT_THEME.theme,
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
