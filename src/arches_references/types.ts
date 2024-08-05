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

// From PrimeVue, not importable directly
export interface FileContentProps {
    files: [];
    badgeSeverity: string;
    badgeValue: string;
    previewWidth: number;
    templates: null;
}
