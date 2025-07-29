import type { AliasedNodeData } from "@/arches_component_lab/types.ts";

export interface URLValue extends AliasedNodeData {
    display_value: string;
    node_value: {
        url: string;
        url_label: string;
    };
    details: never[];
}
