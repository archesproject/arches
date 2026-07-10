import type { Component } from "vue";
import type { Translations } from "vue3-gettext";

export type { ArchesThemeConfiguration } from "@/arches_component_lab/themes/types";

import type { ArchesThemeConfiguration } from "@/arches_component_lab/themes/types";

export interface CreateVueApplicationOptions {
    component: Component;
    themeConfiguration?: ArchesThemeConfiguration;
    initialProps?: Record<string, unknown>;
}

export interface I18nResponse {
    enabled_languages: Record<string, string>;
    language: string;
    translations: Translations;
}
