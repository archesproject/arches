// Injection keys
import type { ControlledList } from "@/types/ControlledListManager";
// Cannot import this from vue? 🤔
// eslint-disable-next-line @typescript-eslint/no-unused-vars, @typescript-eslint/ban-types
interface InjectionKey<T> extends Symbol {}

export const displayedListKey = Symbol() as InjectionKey<ControlledList | null>;

// Constants
export const PREF_LABEL = "prefLabel";
export const ALT_LABEL = "altLabel";
export const URI = "URI";
