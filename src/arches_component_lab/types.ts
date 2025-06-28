export interface CardXNodeXWidget {
    card: {
        name: string;
    };
    config: unknown;
    id: string;
    label: string;
    node: {
        alias: string;
        isrequired: boolean;
    };
    sortorder: number;
    visible: boolean;
    widget: {
        component: string;
    };
}

export interface Language {
    code: string;
    default_direction: "ltr" | "rtl";
    id: number;
    isdefault: boolean;
    name: string;
    scope: string;
}

export interface Label {
    value: string;
    language_id: string;
    valuetype_id: string;
}

export interface WithLabels {
    labels: Label[];
}

export interface WithValues {
    values: Label[];
}

export type Labellable = WithLabels | WithValues;
