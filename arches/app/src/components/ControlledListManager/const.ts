import type { ControlledList, ControlledListItem } from "@/types/ControlledListManager";
import type { Language } from "@/types/arches";

// Injection keys
// Cannot import this from vue? 🤔
// eslint-disable-next-line @typescript-eslint/no-unused-vars, @typescript-eslint/ban-types
interface InjectionKey<T> extends Symbol {}

export const displayedRowKey = Symbol() as InjectionKey<ControlledList | null>;
export const itemKey = Symbol() as InjectionKey<ControlledListItem | null>;
export const selectedLanguageKey = Symbol() as InjectionKey<Language | null>;

// Constants
export const PREF_LABEL = "prefLabel";
export const ALT_LABEL = "altLabel";
export const URI = "URI";
