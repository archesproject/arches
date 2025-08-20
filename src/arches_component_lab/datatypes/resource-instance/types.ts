import type { AliasedNodeData } from "@/arches_component_lab/types.ts";

export interface ResourceInstanceValue extends AliasedNodeData {
    display_value: string;
    node_value: ResourceInstanceReference | null;
    details: { display_value: string; resource_id: string }[];
}

export interface ResourceInstanceReference {
    resourceId: string;
    ontologyProperty?: string;
    resourceXresourceId?: string;
    inverseOntologyProperty?: string;
}

export interface ResourceInstanceDataItem {
    display_value: string;
    order_field: number;
    resourceinstanceid: string;
}

export interface ResourceInstanceSelectOption {
    display_value: string;
    resource_id: string;
}
