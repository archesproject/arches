import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";
import type { NodeData } from "@/arches_component_lab/types.ts";

export interface DateDatatypeCardXNodeXWidgetData extends CardXNodeXWidget {
    node: CardXNodeXWidget["node"] & {
        config: {
            dateFormat: string;
        };
    };
}

export interface DateData extends NodeData {
    display_value: string;
    node_value: string | null;
    details: never[];
}
