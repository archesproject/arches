import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";

export interface DateDatatypeCardXNodeXWidgetData extends CardXNodeXWidget {
    node: CardXNodeXWidget["node"] & {
        config: {
            dateFormat: string;
        };
    };
}
