import type { TreeNode } from "primevue/treenode";

import type {
    AliasedNodeData,
    CardXNodeXWidgetData,
} from "@/arches_vue_components/types.ts";

export interface ReferenceSelectDatatypeCardXNodeXWidgetData
    extends CardXNodeXWidgetData {
    node: CardXNodeXWidgetData["node"] & {
        config: {
            controlledList: string;
            multiValue: boolean;
        };
    };
}

export type ReferenceSelectValue = ReferenceSelectNodeValue[];

export interface ReferenceSelectNodeValue {
    list_id: string;
    uri: string;
    labels: ReferenceSelectLabel[];
}

export interface ReferenceSelectDetails {
    children: ReferenceSelectNodeValue[];
    display_value: string;
    list_item_id: string;
    list_item_values: ReferenceSelectLabel[];
    sortorder: number;
    uri: string;
}

export interface ReferenceSelectLabel {
    id: string;
    language_id: string;
    list_item_id: string;
    value: string;
    valuetype_id: string;
}

export interface ReferenceSelectTreeNode extends TreeNode {
    key: string;
    label: string;
    children: ReferenceSelectTreeNode[];
    data: ReferenceSelectDetails;
}

export interface ReferenceSelectAliasedNodeData extends AliasedNodeData {
    node_value: ReferenceSelectNodeValue[] | null;
    details: ReferenceSelectDetails[];
}
