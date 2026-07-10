import type {
    AliasedNodeData,
    CardXNodeXWidgetData,
} from "@/arches_component_lab/types.ts";

export interface DateCardXNodeXWidgetData extends CardXNodeXWidgetData {
    node: CardXNodeXWidgetData["node"] & {
        config: {
            dateFormat: string;
        };
    };
    config: CardXNodeXWidgetData["config"] & {
        viewMode: string;
        minDate: boolean;
        maxDate: boolean;
    };
}

export interface DateAliasedNodeData extends AliasedNodeData {
    node_value: string | null;
    details: never[];
}
