import type {
    AliasedNodeData,
    CardXNodeXWidgetData,
} from "@/arches_vue_components/types.ts";

export interface DomainCardXNodeXWidgetData extends CardXNodeXWidgetData {
    node: CardXNodeXWidgetData["node"] & {
        config: {
            options: DomainOption[];
        };
    };
}

export interface DomainOption {
    id: string;
    text: string;
    selected: boolean;
}

export interface DomainAliasedNodeData extends AliasedNodeData {
    node_value: string | null;
    details: never[];
}

export interface DomainListAliasedNodeData extends AliasedNodeData {
    node_value: string[] | null;
    details: never[];
}
