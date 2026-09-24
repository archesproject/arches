import type { AliasedNodeData } from "@/arches_vue_components/types.ts";

export interface EDTFAliasedNodeData extends AliasedNodeData {
    node_value: string | null;
    details: never[];
}
