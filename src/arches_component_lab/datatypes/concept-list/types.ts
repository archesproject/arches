import type { AliasedNodeData } from "@/arches_component_lab/types.ts";
import type { CollectionItem } from "@/arches_component_lab/datatypes/concept/types.ts";

export type {
    ConceptFetchResult,
    CollectionItem,
} from "@/arches_component_lab/datatypes/concept/types.ts";

export interface ConceptListAliasedNodeData extends AliasedNodeData {
    node_value: string[] | null;
    details: CollectionItem[];
}
