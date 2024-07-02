import type { Ref } from "vue";

export interface Value {
    id: string;
    valuetype_id: string;
    language_id: string;
    value: string;
    item_id: string;
}

export interface NewValue {
    id: number;
    valuetype_id: string;
    language_id: string;
    value: string;
    item_id: string | number;
}

export type NewOrExistingValue = Value | NewValue;
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
    id: number;
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
    item_id: string;
    url: string;
    metadata: NewOrExistingControlledListItemImageMetadata[];
}

export interface ControlledListItem {
    id: string;
    list_id: string;
    uri: string;
    sortorder: number;
    guide: boolean;
    values: NewOrExistingValue[];
    images: ControlledListItemImage[];
    children: ControlledListItem[];
    parent_id: string | null;
    depth: number;
}

export interface NewControlledListItem {
    id: number;
    list_id: string;
    uri: string;
    sortorder: number;
    guide: boolean;
    values: NewOrExistingValue[];
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

export interface NewControlledList {
    id: number;
    name: string;
    dynamic: boolean;
    search_only: boolean;
    items: ControlledListItem[];
    nodes: ReferencingNode[];
}

export type Selectable =
    | ControlledList
    | ControlledListItem
    | NewControlledList
    | NewControlledListItem;

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

// Prop injection types
export interface DisplayedRowRefAndSetter {
    displayedRow: Ref<Selectable | null>;
    setDisplayedRow: (val: Selectable | null) => void;
}

export interface DisplayedListRefAndSetter {
    displayedRow: Ref<ControlledList | null>;
    setDisplayedRow: (val: Selectable | null) => void;
}

export interface DisplayedListItemRefAndSetter {
    displayedRow: Ref<ControlledListItem | null>;
    setDisplayedRow: (val: Selectable | null) => void;
}

// From PrimeVue, not importable directly
export interface FileContentProps {
    files: [];
    badgeSeverity: string;
    badgeValue: string;
    previewWidth: number;
    templates: null;
}
