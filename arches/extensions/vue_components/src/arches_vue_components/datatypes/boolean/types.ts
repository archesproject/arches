import type { AliasedNodeData } from "@/arches_vue_components/types.ts";

export interface BooleanAliasedNodeData extends AliasedNodeData {
    node_value: boolean | null;
    details: never[];
}
