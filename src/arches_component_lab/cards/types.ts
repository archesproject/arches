import { defineAsyncComponent } from "vue";
import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";

export interface WidgetConfiguration {
    component: typeof defineAsyncComponent;
    cardXNodeXWidgetDatum: CardXNodeXWidget;
}
