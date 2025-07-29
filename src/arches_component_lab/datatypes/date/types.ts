import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { AliasedNodeData } from "@/arches_component_lab/types.ts";

export interface DateDatatypeCardXNodeXWidgetData extends CardXNodeXWidgetData {
    node: CardXNodeXWidgetData["node"] & {
        config: {
            dateFormat: string;
        };
    };
}

export interface DateValue extends AliasedNodeData {
    display_value: string;
    node_value: string | null;
    details: never[];
}
