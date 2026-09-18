import type { InjectionKey, Ref } from "vue";
import type {
    ControlledListItem,
    DisplayedRowRefAndSetter,
    IsEditingRefAndSetter,
    Language,
} from "@/arches_controlled_lists/types";

// Injection keys
export const displayedRowKey =
    Symbol() as InjectionKey<DisplayedRowRefAndSetter>;
export const isEditingKey = Symbol() as InjectionKey<IsEditingRefAndSetter>;
export const itemKey = Symbol() as InjectionKey<Ref<ControlledListItem>>;
export const selectedLanguageKey = Symbol() as InjectionKey<Ref<Language>>;
export const systemLanguageKey = Symbol() as InjectionKey<Language>;

// Constants
export const NOTE = "note";
export const URI = "URI";
export const CONTRAST = "contrast";
export const ERROR = "error";
export const DANGER = "danger";
export const PRIMARY = "primary";
export const SECONDARY = "secondary";
export const SUCCESS = "success";
export const DEFAULT_ERROR_TOAST_LIFE = 8000;

export const PREF_LABEL = "prefLabel";
export const ALT_LABEL = "altLabel";
export const HIDDEN_LABEL = "hiddenLabel";

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

// Temporary workaround until received from backend
export const ENGLISH = {
    code: "en",
    default_direction: "ltr" as const,
    id: 1,
    isdefault: true,
    name: "English",
    scope: "system",
};
