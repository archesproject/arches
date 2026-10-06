import type { AliasedNodeData } from "@/arches_vue_components/types.ts";

export interface URLNodeValue {
    url: string;
    url_label: string;
}

export interface URLAliasedNodeData extends AliasedNodeData {
    node_value: URLNodeValue | null;
    details: never[];
}
