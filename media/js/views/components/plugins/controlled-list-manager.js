import ko from 'knockout';
import { definePreset } from '@primevue/themes';
import Aura from '@primevue/themes/aura';

import ControlledListManager from '@/arches_references/plugins/ControlledListManager.vue';
import createVueApplication from 'utils/create-vue-application';
import ControlledListManagerTemplate from 'templates/views/components/plugins/controlled-list-manager.htm';

// Much of this might get merged upstream to core arches in 8.0?
const ControlledListsPreset = definePreset(Aura, {
    primitive: {
        sky: {
            950: '#2d3c4b',
        },
    },
    components: {
        button: {
            root: {
                label: {
                    fontWeight: 600,
                },
            },
        },
        datatable: {
            column: {
                title: {
                    fontWeight: 600,
                },
            },
        },
        splitter: {
            handle: {
                background: "{surface.500}",
            },
        },
    },
});

const controlledListsTheme = {
    theme: {
        preset: ControlledListsPreset,
        options: {
            prefix: 'p',
            darkModeSelector: 'system',
            cssLayer: false
        },
    },
};

ko.components.register('controlled-list-manager', {
    viewModel: function() {
        createVueApplication(ControlledListManager, controlledListsTheme).then((vueApp) => {
            vueApp.mount('#controlled-list-manager-mounting-point');
        });
    },
    template: ControlledListManagerTemplate,
});
