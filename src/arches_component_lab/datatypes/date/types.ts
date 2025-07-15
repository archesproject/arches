import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";

export interface DateDatatypeCardXNodeXWidgetData extends CardXNodeXWidget {
    config: CardXNodeXWidget["config"] & {
        dateFormat: string;
        datePickerDisplayConfiguration: {
            dateFormat: string;
            shouldShowTime: boolean;
        };
    };
}
