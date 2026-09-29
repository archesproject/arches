import type { AliasedNodeData } from "@/arches_vue_components/types.ts";

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

export interface ConceptValueItem {
    concept_id: string;
    language_id: string;
    value: string;
    valueid: string;
    valuetype_id: string;
}

export interface ConceptAliasedNodeData extends AliasedNodeData {
    node_value: string | null;
    details: ConceptValueItem[] | [];
}
