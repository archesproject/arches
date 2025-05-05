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
