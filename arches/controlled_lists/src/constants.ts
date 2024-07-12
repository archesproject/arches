import type { InjectionKey } from "vue";
import type { Language } from "@/arches/types";
import type {
    ControlledList,
    ControlledListItem,
} from "@/controlled-lists/types";

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
export const SUCCESS = "success";
export const DEFAULT_ERROR_TOAST_LIFE = 8000;

// Django model choices
export const METADATA_CHOICES = {
    title: "title",
    alternativeText: "alt",
    description: "desc",
    attribution: "attr",
};

export const NOTE_CHOICES = {
    scope: "scopeNote",
    definition: "definition",
    example: "example",
    history: "historyNote",
    editorial: "editorialNote",
    change: "changeNote",
    note: "note",
    description: "description",
};
