import type {
    AliasedNodeData,
    CardXNodeXWidgetData,
} from "@/arches_component_lab/types.ts";

export interface NumberCardXNodeXWidgetData extends CardXNodeXWidgetData {
    config: CardXNodeXWidgetData["config"] & {
        prefix?: string;
        suffix?: string;
        min?: number;
        max?: number;
        step?: number;
        precision?: string | number;
    };
}

export interface NumberAliasedNodeData extends AliasedNodeData {
    node_value: number | null;
    details: never[];
}
