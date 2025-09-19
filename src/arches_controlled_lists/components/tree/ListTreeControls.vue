<script setup lang="ts">
import ActionBanner from "@/arches_controlled_lists/components/tree/ActionBanner.vue";
import AddDeleteControls from "@/arches_controlled_lists/components/tree/AddDeleteControls.vue";
import PresentationControls from "@/arches_controlled_lists/components/tree/PresentationControls.vue";

import type { TreeExpandedKeys, TreeSelectionKeys } from "primevue/tree";
import type { TreeNode } from "primevue/treenode";
import type { ControlledList } from "@/arches_controlled_lists/types";

const controlledListItemsTree = defineModel<TreeNode[]>("tree", {
    required: true,
});
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
const shouldCopyChildren = defineModel<boolean>("shouldCopyChildren", {
    required: true,
});
const nextNewList = defineModel<ControlledList>("nextNewList");
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
        expandedKeys.value[node.key] = true;

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
        v-model:should-copy-children="shouldCopyChildren"
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
    flex-direction: column;
    background: var(--p-content-hover-background);
    gap: 0rem;
    padding: 0;
    justify-content: space-between;
}
</style>
