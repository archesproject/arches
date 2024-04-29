export type Label = {
    id: string,
    valuetype_id: string,
    language_id: string,
    value: string,
    item_id: string,
};

export type NewLabel = {
    id: number,
    valuetype_id: string,
    language_id: string,
    value: string,
    item_id: string,
};

export type ValueType = "prefLabel" | "altLabel";

export type ControlledListItemImageMetadata = {
    id: string,
    controlled_list_item_image_id: string,
    language_id: string,
    metadata_type: string,
    metadata_label: string,
    value: string,
};

export type NewControlledListItemImageMetadata = {
    id: number,
    controlled_list_item_image_id: string,
    language_id: string,
    metadata_type: string,
    metadata_label: string,
    value: string,
};

export type MetadataChoice = {
    type: 'title' | 'desc' | 'attr' | 'alt',
    label: string,
};

export type ControlledListItemImage = {
    id: string,
    item_id: string,
    url: string,
    metadata: ControlledListItemImageMetadata[],
};

export type ControlledListItem = {
    id: string,
    controlled_list_id: string,
    uri: string,
    sortorder: number,
    guide: boolean,
    labels: Label[],
    images: ControlledListItemImage[],
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
    graph_name: string,
};
