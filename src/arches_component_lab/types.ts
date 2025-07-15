export interface NodeData {
    display_value: string;
    interchange_value: unknown;
}

export interface CardXNodeXWidget {
    card: {
        name: string;
    };
    config: {
        defaultValue: unknown | null;
        placeholder: unknown | null;
    };
    id: string;
    label: string;
    node: {
        alias: string;
        isrequired: boolean;
        nodeid: string;
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
