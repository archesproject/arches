<script setup lang="ts">
import ActionBanner from "@/controlledlists/components/tree/ActionBanner.vue";
import AddDeleteControls from "@/controlledlists/components/tree/AddDeleteControls.vue";
import PresentationControls from "@/controlledlists/components/tree/PresentationControls.vue";

import type { TreeExpandedKeys, TreeSelectionKeys } from "primevue/tree/Tree";
import type { TreeNode } from "primevue/treenode";
import type { NewControlledList } from "@/controlledlists/types";

const controlledListItemsTree = defineModel<TreeNode[]>({ required: true });
const rerenderTree = defineModel<number>("rerenderTree", { required: true });
const expandedKeys = defineModel<TreeExpandedKeys>("expandedKeys", {
    required: true,
});
const selectedKeys = defineModel<TreeSelectionKeys>("selectedKeys", {
    required: true,
});
const movingItem = defineModel<TreeNode>("movingItem");
const isMultiSelecting = defineModel<boolean>("isMultiSelecting", {
    required: true,
});
const nextNewList = defineModel<NewControlledList>("nextNewList");
const newListFormValue = defineModel<string>("newListFormValue", {
    required: true,
});

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
        />
    </div>
    <ActionBanner
        v-if="movingItem || isMultiSelecting"
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
