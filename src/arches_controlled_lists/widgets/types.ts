import type { Value } from "@/arches_controlled_lists/types.ts";
import type { TreeNode } from "primevue/treenode";

export type WidgetMode = "edit" | "view";

export interface ControlledListItemTileValue {
    list_id: string;
    uri: string;
    values: Value[];
}

export interface ReferenceSelectFetchedOption {
    list_item_id: string;
    display_value: string;
    sort_order: number;
    children: ReferenceSelectFetchedOption[];
}

export interface ReferenceSelectTreeNode extends TreeNode {
    key: string;
    label: string;
    sort_order: number;
    children: ReferenceSelectTreeNode[];
    data: ReferenceSelectFetchedOption;
}
