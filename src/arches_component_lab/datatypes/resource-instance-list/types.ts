import type { AliasedTileNodeValue } from "@/arches_component_lab/types.ts";

export interface ResourceInstanceListValue extends AliasedTileNodeValue {
    display_value: string;
    node_value: {
        inverseOntologyProperty: string;
        ontologyProperty: string;
        resourceId: string;
        resourceXresourceId: string;
    }[];
    details: { display_value: string; resource_id: string }[];
}
