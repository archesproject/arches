import ko from 'knockout';

import { definePreset, palette } from '@primeuix/themes';
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
        colorScheme: {
            light: {
                primary: palette(ArchesPreset.primitive.arches.blue),
                dialog: {
                    headerTextColor: "{slate.50}",
                },  
            },
            dark: {
                dialog: {
                    headerTextColor: "{slate.50}",
                },
            },
        },
    },
    components: {
        button: {
            colorScheme: {
                light: {
                    primary: {
                        background: "{primary-800}",
                        borderColor: "{button-primary-background}",
                    },
                    danger: {
                        background: "{orange-700}",
                        borderColor: "{orange-700}",
                        hover: {
                            background: "{orange-500}",
                            borderColor: "{orange-500}",
                        },
                    },
                },
            },
            root: {
                label: {
                    fontWeight: 600,
                },
            },
            border: {
                radius: '.25rem',
            },
        },
        toast: {
            summary: { fontSize: '1.5rem' },
            detail: { fontSize: '1.25rem' },
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
