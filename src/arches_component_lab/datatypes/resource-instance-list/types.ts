import type { AliasedNodeData } from "@/arches_component_lab/types.ts";

export interface ResourceInstanceListValue extends AliasedNodeData {
    display_value: string;
    node_value: {
        inverseOntologyProperty: string;
        ontologyProperty: string;
        resourceId: string;
        resourceXresourceId: string;
    }[];
    details: { display_value: string; resource_id: string }[];
}
