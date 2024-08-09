import PrimeVue from 'primevue/config';
import AnimateOnScroll from 'primevue/animateonscroll';
import ConfirmationService from 'primevue/confirmationservice';
import DialogService from 'primevue/dialogservice';
import FocusTrap from 'primevue/focustrap';
import StyleClass from 'primevue/styleclass';
import ToastService from 'primevue/toastservice';
import Tooltip from 'primevue/tooltip';

import { definePreset } from '@primevue/themes';
import { createApp } from 'vue';
import { createGettext } from "vue3-gettext";
import Aura from '@primevue/themes/aura';

import arches from 'arches';

export const ArchesPreset = definePreset(Aura, {
    primitive: {
        sky: {
            950: '#2d3c4b',  // matches arches sidebar
        },
    },
    semantic: {
        primary: {
            50: '{sky.50}',
            100: '{sky.100}',
            200: '{sky.200}',
            300: '{sky.300}',
            400: '{sky.400}',
            500: '{sky.500}',
            600: '{sky.600}',
            700: '{sky.700}',
            800: '{sky.800}',
            900: '{sky.900}',
            950: '{sky.950}',
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
                background: '{surface.500}',
            },
        },
    },
});

const DEFAULT_THEME = {
    theme: {
        preset: ArchesPreset,
        options: {
            prefix: 'p',
            darkModeSelector: 'system',
            cssLayer: false
        }
    }
};

export default async function createVueApplication(vueComponent, themeConfiguration) {
    /**
     * This wrapper allows us to maintain a level of control inside arches-core
     * over Vue apps. For instance this allows us to abstract i18n setup/config
     * away from app initialization, and also allows us to ensure any plugins 
     * we'd like to use across the Arches ecosystem will be available. This also
     * Vue apps more easily extensible if we choose to add plugins or logic in
     * the future.
    **/

    /**
     * TODO: cbyrd #10501 - we should add an event listener that will re-fetch i18n data
     * and rebuild the app when a specific event is fired from the LanguageSwitcher component.
    **/
    return fetch(arches.urls.api_get_frontend_i18n_data).then(function(resp) {
        if (!resp.ok) {
            throw new Error(resp.statusText);
        }
        return resp.json();
    }).then(function(respJSON) {
        const gettext = createGettext({
            availableLanguages: respJSON['enabled_languages'],
            defaultLanguage: respJSON['language'],
            translations: respJSON['translations'],
        });

        const app = createApp(vueComponent);

        app.use(PrimeVue, themeConfiguration || DEFAULT_THEME);
        app.use(gettext);
        app.use(ConfirmationService);
        app.use(DialogService);
        app.use(ToastService);
        app.directive('animateonscroll', AnimateOnScroll);
        app.directive('focustrap', FocusTrap);
        app.directive('styleclass', StyleClass);
        app.directive('tooltip', Tooltip);

        return app;
    });
}
