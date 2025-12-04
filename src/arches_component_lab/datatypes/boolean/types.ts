import type { AliasedNodeData } from "@/arches_component_lab/types.ts";

export interface BooleanValue extends AliasedNodeData {
    display_value: string;
    node_value: boolean | null;
    details: never[];
}
