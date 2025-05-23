import { defineAsyncComponent } from "vue";

export interface CardXNodeXWidgetDatum {
    card: {
        name: string;
    };
    id: string;
    node: {
        alias: string;
    };
    widget: {
        component: string;
    };
}

export interface WidgetConfiguration {
    component: typeof defineAsyncComponent;
    cardXNodeXWidgetDatum: CardXNodeXWidgetDatum;
}
