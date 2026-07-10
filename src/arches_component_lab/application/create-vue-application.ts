import { createApp } from "vue";

import PrimeVue from "primevue/config";
import AnimateOnScroll from "primevue/animateonscroll";
import ConfirmationService from "primevue/confirmationservice";
import DialogService from "primevue/dialogservice";
import FocusTrap from "primevue/focustrap";
import StyleClass from "primevue/styleclass";
import ToastService from "primevue/toastservice";
import Tooltip from "primevue/tooltip";

import { createPinia } from "pinia";
import { createGettext } from "vue3-gettext";

import { DEFAULT_THEME } from "@/arches_component_lab/themes";
import { generateArchesURL } from "@/arches_component_lab/application/generate-arches-url";

import type { App } from "vue";
import type {
    CreateVueApplicationOptions,
    I18nResponse,
} from "@/arches_component_lab/application/types";

export async function createVueApplication({
    component,
    themeConfiguration = DEFAULT_THEME,
    initialProps = {},
}: CreateVueApplicationOptions): Promise<App<Element>> {
    const response = await fetch(
        generateArchesURL("arches:get_frontend_i18n_data"),
    );
    if (!response.ok) {
        throw new Error(response.statusText);
    }

    const i18nData = (await response.json()) as I18nResponse;

    const gettext = createGettext({
        availableLanguages: i18nData.enabled_languages,
        defaultLanguage: i18nData.language,
        translations: i18nData.translations,
        silent: true,
    });

    const pinia = createPinia();
    const app = createApp(component, initialProps);

    const darkModeClass =
        themeConfiguration.theme.options.darkModeSelector.substring(1);
    const darkModeStorageKey = `arches.${darkModeClass}`;
    const darkModeToggleState = localStorage.getItem(darkModeStorageKey);
    if (
        darkModeToggleState === "true" ||
        (darkModeToggleState === null &&
            window.matchMedia("(prefers-color-scheme: dark)").matches)
    ) {
        document.documentElement.classList.add(darkModeClass);
    }

    app.use(PrimeVue, themeConfiguration);
    app.use(gettext);
    app.use(pinia);
    app.use(ConfirmationService);
    app.use(DialogService);
    app.use(ToastService);
    app.directive("animateonscroll", AnimateOnScroll);
    app.directive("focustrap", FocusTrap);
    app.directive("styleclass", StyleClass);
    app.directive("tooltip", Tooltip);

    return app;
}
