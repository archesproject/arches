import type { Ref } from "vue";

export interface Value {
    id: string;
    valuetype_id: string;
    language_id: string;
    value: string;
    list_item_id: string;
}

export interface NewValue {
    id: null;
    valuetype_id: string;
    language_id: string;
    value: string;
    list_item_id: string;
}

export type ValueCategory = string;
export type ValueType = string;

export interface ControlledListItemImageMetadata {
    id: string;
    list_item_image_id: string;
    language_id: string;
    metadata_type: string;
    metadata_label: string;
    value: string;
}

export interface NewControlledListItemImageMetadata {
    id: null;
    list_item_image_id: string;
    language_id: string;
    metadata_type: string;
    metadata_label: string;
    value: string;
}

export type NewOrExistingControlledListItemImageMetadata =
    | ControlledListItemImageMetadata
    | NewControlledListItemImageMetadata;

export interface LabeledChoice {
    type: string;
    label: string;
}

export interface ControlledListItemImage {
    id: string;
    list_item_id: string;
    url: string;
    metadata: ControlledListItemImageMetadata[];
}

export interface ControlledListItem {
    id: string;
    list_id: string;
    uri: string;
    sortorder: number;
    guide: boolean;
    values: Value[];
    images: ControlledListItemImage[];
    children: ControlledListItem[];
    parent_id: string;
    depth: number;
}

export interface NewControlledListItem {
    id: null;
    list_id: string;
    uri: string;
    sortorder: number;
    guide: boolean;
    values: Value[];
    images: ControlledListItemImage[];
    children: ControlledListItem[];
    parent_id: string | null;
    depth: number;
}

export interface ControlledList {
    id: string;
    name: string;
    dynamic: boolean;
    search_only: boolean;
    items: ControlledListItem[];
    nodes: ReferencingNode[];
}

export type Selectable =
    | ControlledList
    | ControlledListItem
    | NewControlledListItem;

export type RowSetter = (val: Selectable | null) => void;

export interface ReferencingNode {
    id: string;
    name: string;
    nodegroup_id: string;
    graph_id: string;
    graph_name: string;
}

export interface MoveLabels {
    addChild: string;
    moveUp: string;
    moveDown: string;
    changeParent: string;
}

export interface IconLabels {
    list: string;
    item: string;
}

// For force-casting injection types (to type-narrow undefined)
type DisplayedRowRef = Ref<
    ControlledList | ControlledListItem | NewControlledListItem | null
>;
type DisplayedRowSetter = (
    DisplayedRowRef:
        | ControlledList
        | ControlledListItem
        | NewControlledListItem
        | null,
) => void;
export type DisplayedRowRefAndSetter = {
    displayedRow: DisplayedRowRef;
    setDisplayedRow: DisplayedRowSetter;
};

export type IsEditingRefAndSetter = {
    isEditing: Ref<boolean>;
    setIsEditing: (editing: boolean) => void;
};
