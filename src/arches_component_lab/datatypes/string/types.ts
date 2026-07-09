import type { AliasedNodeData } from "@/arches_component_lab/types.ts";

export interface LanguageValue {
    value: string;
    direction: "ltr" | "rtl";
}

export interface StringAliasedNodeData extends AliasedNodeData {
    node_value: Record<string, LanguageValue> | null;
    details: never[];
}
