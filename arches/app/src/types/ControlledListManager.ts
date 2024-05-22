import type { Ref } from "vue";

export type Value = {
    id: string,
    valuetype_id: string,
    language_id: string,
    value: string,
    item_id: string,
};

export type NewValue = {
    id: number,
    valuetype_id: string,
    language_id: string,
    value: string,
    item_id: string,
};

export type NewOrExistingValue = Value | NewValue;
export type ValueCategory = string;
export type ValueType = string;

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

export type NewOrExistingControlledListItemImageMetadata = (
    ControlledListItemImageMetadata | NewControlledListItemImageMetadata
);

export type MetadataChoice = {
    type: 'title' | 'desc' | 'attr' | 'alt',
    label: string,
};

export type ControlledListItemImage = {
    id: string,
    item_id: string,
    url: string,
    metadata: NewOrExistingControlledListItemImageMetadata[],
};

export type ControlledListItem = {
    id: string,
    controlled_list_id: string,
    uri: string,
    sortorder: number,
    guide: boolean,
    values: NewOrExistingValue[],
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

// Prop injection types
export interface DisplayedRowRefAndSetter {
    displayedRow: Ref<Selectable | null>;
    setDisplayedRow: (val: Selectable | null) => void;
};

export interface DisplayedListRefAndSetter {
    displayedRow: Ref<ControlledList | null>;
    setDisplayedRow: (val: Selectable | null) => void;
};

export interface DisplayedListItemRefAndSetter {
    displayedRow: Ref<ControlledListItem | null>;
    setDisplayedRow: (val: Selectable | null) => void;
};
