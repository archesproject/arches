import type { AliasedNodeData } from "@/arches_vue_components/types.ts";

export interface NonLocalizedTextAliasedNodeData extends AliasedNodeData {
    node_value: string | null;
    details: never[];
}
