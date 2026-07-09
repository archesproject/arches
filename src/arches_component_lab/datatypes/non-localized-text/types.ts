import type { AliasedNodeData } from "@/arches_component_lab/types.ts";

export interface NonLocalizedTextAliasedNodeData extends AliasedNodeData {
    node_value: string | null;
    details: never[];
}
