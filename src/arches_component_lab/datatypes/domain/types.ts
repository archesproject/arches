import type {
    AliasedNodeData,
    CardXNodeXWidgetData,
} from "@/arches_component_lab/types.ts";

export interface DomainDatatypeCardXNodeXWidgetData
    extends CardXNodeXWidgetData {
    node: CardXNodeXWidgetData["node"] & {
        config: {
            options: DomainOption[];
        };
    };
}
export interface DomainValue extends AliasedNodeData {
    display_value: string;
    node_value: string | null;
    details: never[];
}

export interface DomainValueList extends AliasedNodeData {
    display_value: string;
    node_value: string[] | null;
    details: never[];
}

export interface DomainOption {
    id: string;
    text: string;
    selected: boolean;
}
