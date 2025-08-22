import type { TreeNode } from "primevue/treenode";

import type { AliasedNodeData } from "@/arches_component_lab/types.ts";
import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";

export interface ReferenceSelectDatatypeCardXNodeXWidgetData
    extends CardXNodeXWidgetData {
    node: CardXNodeXWidgetData["node"] & {
        config: {
            controlledList: string;
            multiValue: boolean;
        };
    };
}

export interface ReferenceSelectValue extends AliasedNodeData {
    display_value: string;
    node_value: ReferenceSelectNodeValue[];
    details: ReferenceSelectDetails[];
}

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
