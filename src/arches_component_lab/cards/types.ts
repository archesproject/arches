import type { Component } from "vue";
import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";

export interface WidgetConfiguration {
    component: Component;
    cardXNodeXWidgetDatum: CardXNodeXWidget;
}
