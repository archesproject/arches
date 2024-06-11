<script setup lang="ts">
import ActionBanner from "@/components/ControlledListManager/tree/ActionBanner.vue";
import AddDeleteControls from "@/components/ControlledListManager/tree/AddDeleteControls.vue";
import PresentationControls from "@/components/ControlledListManager/tree/PresentationControls.vue";

import type { TreeExpandedKeys, TreeSelectionKeys } from "primevue/tree/Tree";
import type { TreeNode } from "primevue/treenode";
import type { NewControlledList } from "@/types/ControlledListManager";

const controlledListItemsTree = defineModel<TreeNode[]>({ required: true });
const rerenderTree = defineModel<number>("rerenderTree", { required: true });
const expandedKeys = defineModel<TreeExpandedKeys>("expandedKeys", { required: true });
const selectedKeys = defineModel<TreeSelectionKeys>("selectedKeys", { required: true });
const movingItem = defineModel<TreeNode>("movingItem", { required: true });
const isMultiSelecting = defineModel<boolean>("isMultiSelecting", { required: true });
const nextNewList = defineModel<NewControlledList>("nextNewList");
const newListFormValue = defineModel<string>("newListFormValue", { required: true });
const newListCounter = defineModel<number>("newListCounter", { required: true });

const expandAll = () => {
    for (const node of controlledListItemsTree.value) {
        expandNode(node);
    }
};

const collapseAll = () => {
    expandedKeys.value = {};
};

const expandNode = (node: TreeNode) => {
    if (node.children && node.children.length) {
        expandedKeys.value[node.key as string] = true;

        for (const child of node.children) {
            expandNode(child);
        }
    }
};
</script>

<template>
    <div class="controls">
        <AddDeleteControls
            v-model="controlledListItemsTree"
            v-model:is-multi-selecting="isMultiSelecting"
            v-model:selected-keys="selectedKeys"
            v-model:next-new-list="nextNewList"
            v-model:new-list-form-value="newListFormValue"
            v-model:new-list-counter="newListCounter"
        />
    </div>
    <ActionBanner
        v-if="movingItem.key || isMultiSelecting"
        v-model:is-multi-selecting="isMultiSelecting"
        v-model:moving-item="movingItem"
        v-model:rerender-tree="rerenderTree"
        v-model:selected-keys="selectedKeys"
    />
    <div
        v-else
        class="controls"
    >
        <PresentationControls
            :controlled-list-items-tree
            :expand-all
            :collapse-all
        />
    </div>
</template>

<style scoped>
.controls {
    display: flex;
    background: #f3fbfd;
    gap: 0.5rem;
    font-size: small;
    padding: 0.5rem;
    justify-content: space-between;
}
</style>
