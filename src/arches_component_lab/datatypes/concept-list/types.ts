import type { AliasedNodeData } from "@/arches_component_lab/types.ts";
import type {
    ConceptFetchResult,
    CollectionItem,
} from "@/arches_component_lab/datatypes/concept/types.ts";

export type { ConceptFetchResult, CollectionItem };

export interface ConceptListValue extends AliasedNodeData {
    display_value: string;
    node_value: string[];
    details: CollectionItem[];
}
