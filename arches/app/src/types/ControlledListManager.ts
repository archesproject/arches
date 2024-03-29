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
    guide: boolean,
    labels: Label[],
    children: ControlledListItem[],
    parent_id: string,
    depth: number,
};

export type NewItem = {
    parent_id: string,  // list or item
};

export type ControlledList = {
    id: string,
    name: string,
    dynamic: boolean,
    search_only: boolean,
    items: ControlledListItem[],
    nodes: ReferencingNode[],
};

export type Selectable = ControlledList | ControlledListItem;

export type ReferencingNode = {
    id: string,
    name: string,
    nodegroup_id: string,
    graph_id: string,
};
