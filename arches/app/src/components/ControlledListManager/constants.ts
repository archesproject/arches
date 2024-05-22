import type { InjectionKey } from "vue";
import type { ControlledList, ControlledListItem } from "@/types/ControlledListManager";
import type { Language } from "@/types/arches";

export const displayedRowKey = Symbol() as InjectionKey<ControlledList | null>;
export const itemKey = Symbol() as InjectionKey<ControlledListItem | null>;
export const selectedLanguageKey = Symbol() as InjectionKey<Language | null>;

// Constants
export const PREF_LABEL = "prefLabel";
export const ALT_LABEL = "altLabel";
export const NOTE = "note";
export const URI = "URI";
export const ERROR = "error";
export const DANGER = "danger";

// Django model choices
export const METADATA_CHOICES = {
    title: 'title',
    alternativeText: 'alt',
    description: 'desc',
    attribution: 'attr',
};
