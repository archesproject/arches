export type Label = {
    id: string,
    valuetype: string,
    language: string,
    value: string,
    item_id: string,
}

export type NewLabel = {
    id: null,
    valuetype: string,
    language: string,
    value: string,
    item_id: string,
}

export type ValueType = "prefLabel" | "altLabel";

export type ControlledListItem = {
    id: string,
    uri: string,
    sortorder: number,
    labels: Label[],
    children: ControlledListItem[],
    parent_id: string,
    depth: number,
};

export type ControlledList = {
    id: string,
    name: string,
    dynamic: boolean,
    items: ControlledListItem[],
};

export type LanguageMap = {
    readonly [index: string]: string;
};
