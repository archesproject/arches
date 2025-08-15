import type { AliasedNodeData } from "@/arches_component_lab/types.ts";

export interface ResourceInstanceValue extends AliasedNodeData {
    display_value: string;
    node_value: ResourceInstanceReference | null;
    details: { display_value: string; resource_id: string }[];
}

export interface ResourceInstanceReference {
    resource_id: string;
    ontologyProperty?: string;
    resourceXresourceId?: string;
    inverseOntologyProperty?: string;
}

export interface ResourceInstanceResult {
    resourceinstanceid: string;
    display_value: string;
}
