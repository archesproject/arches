import type { AliasedNodeData } from "@/arches_vue_components/types.ts";
import type { ConceptValueItem } from "@/arches_vue_components/datatypes/concept/types.ts";

export type {
    ConceptFetchResult,
    CollectionItem,
} from "@/arches_vue_components/datatypes/concept/types.ts";

export interface ConceptListAliasedNodeData extends AliasedNodeData {
    node_value: string[] | null;
    details: ConceptValueItem[] | [];
}
