import type { AliasedNodeData } from "@/arches_component_lab/types.ts";

export interface ConceptFetchResult {
    results: CollectionItem[];
    total_results: number;
}

export interface CollectionItem {
    key: string; // This is "id" in the response JSON
    label: string; // This is "text" in the response JSON
    conceptid: string;
    sortOrder: string;
    children: CollectionItem[];
}

export interface ConceptValue extends AliasedNodeData {
    display_value: string;
    node_value: string | null;
    details: CollectionItem[];
}
