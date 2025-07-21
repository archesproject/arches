import type { AliasedTileNodeValue } from "@/arches_component_lab/types.ts";

export interface ResourceInstanceValue extends AliasedTileNodeValue {
    display_value: string;
    node_value: {
        inverseOntologyProperty: string;
        ontologyProperty: string;
        resourceId: string;
        resourceXresourceId: string;
    };
    details: { display_value: string; resource_id: string }[];
}

export interface ResourceInstanceReference {
    resource_id: string;
    display_value: string;
    interchange_value?: string;
    ontologyProperty?: string;
    resourceXresourceId?: string;
    inverseOntologyProperty?: string;
}

export interface ResourceInstanceResult {
    resourceinstanceid: string;
    display_value: string;
}
