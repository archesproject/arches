import type { AliasedNodeData } from "@/arches_component_lab/types.ts";

export interface BooleanAliasedNodeData extends AliasedNodeData {
    node_value: boolean | null;
    details: never[];
}
