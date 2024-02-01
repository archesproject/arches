export type Label = {
    id: string,
    valuetype: string,
    language: string,
    value: string,
}

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
