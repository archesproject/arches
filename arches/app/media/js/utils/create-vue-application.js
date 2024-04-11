import PrimeVue from 'primevue/config';
import AnimateOnScroll from 'primevue/animateonscroll';
import ConfirmationService from 'primevue/confirmationservice';
import DialogService from 'primevue/dialogservice';
import FocusTrap from 'primevue/focustrap';
import StyleClass from 'primevue/styleclass';
import ToastService from 'primevue/toastservice';
import Tooltip from 'primevue/tooltip';

import { createApp } from 'vue';
import { createGettext } from "vue3-gettext";

export default async function createVueApplication(vueComponent){
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
    return fetch('/api/get_frontend_i18n_data').then(resp => {
        if (!resp.ok) {
            throw new Error(resp.statusText);
        }
        return resp.json();
    }).then(respJSON => {
        const gettext = createGettext({
            availableLanguages: respJSON['enabled_languages'],
            defaultLanguage: respJSON['language'],
            translations: respJSON['translations'],
        });

        const app = createApp(vueComponent);
        app.use(PrimeVue);
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
