import type { AliasedNodeData } from "@/arches_component_lab/types.ts";

export interface LanguageValue extends AliasedNodeData {
    display_value: string;
    node_value: string | null;
    details: never[];
}
