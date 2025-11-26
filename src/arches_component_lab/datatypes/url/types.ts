import type { AliasedNodeData } from "@/arches_component_lab/types.ts";

export interface URL {
    url: string;
    url_label: string;
}
export interface URLValue extends AliasedNodeData {
    display_value: string;
    node_value: URL;
    details: never[];
}
