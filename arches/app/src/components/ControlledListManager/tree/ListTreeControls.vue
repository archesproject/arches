<script setup lang="ts">
import { inject, watch } from "vue";
import { useRoute } from "vue-router";

import {
    displayedRowKey,
    routes,
} from "@/components/ControlledListManager/constants.ts";
import { findNodeInTree } from "@/components/ControlledListManager/utils.ts";
import ActionBanner from "@/components/ControlledListManager/tree/ActionBanner.vue";
import AddDeleteControls from "@/components/ControlledListManager/tree/AddDeleteControls.vue";
import PresentationControls from "@/components/ControlledListManager/tree/PresentationControls.vue";

import type { TreeExpandedKeys, TreeSelectionKeys } from "primevue/tree/Tree";
import type { TreeNode } from "primevue/treenode";
import type {
    DisplayedListItemRefAndSetter,
    NewControlledList,
} from "@/types/ControlledListManager";

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
const movingItem = defineModel<TreeNode>("movingItem", { required: true });
const isMultiSelecting = defineModel<boolean>("isMultiSelecting", {
    required: true,
});
const nextNewList = defineModel<NewControlledList>("nextNewList");
const newListFormValue = defineModel<string>("newListFormValue", {
    required: true,
});

const { setDisplayedRow } = inject(
    displayedRowKey,
) as DisplayedListItemRefAndSetter;

const route = useRoute();

// React to route changes.
// Add list tree as dependency so it runs on initial fetch.
watch(
    [
        () => {
            return { ...route };
        },
        controlledListItemsTree,
    ],
    ([newRoute]) => {
        switch (newRoute.name) {
            case routes.splash:
                setDisplayedRow(null);
                break;
            case routes.list: {
                if (!controlledListItemsTree.value.length) {
                    return;
                }
                const list = controlledListItemsTree.value.find(
                    (node) => node.data.id === newRoute.params.id,
                );
                if (list) {
                    setDisplayedRow(list.data);
                    expandedKeys.value = { [list.data.id]: true };
                    selectedKeys.value = { [list.data.id]: true };
                } else {
                    setDisplayedRow(null);
                }
                break;
            }
            case routes.item: {
                if (!controlledListItemsTree.value.length) {
                    return;
                }
                const { found, path } = findNodeInTree(
                    controlledListItemsTree.value,
                    newRoute.params.id,
                );
                if (found) {
                    setDisplayedRow(found.data);
                    const itemsToExpandIds = path.map(
                        (itemInPath: TreeNode) => itemInPath.key,
                    );
                    expandedKeys.value = Object.fromEntries(
                        [
                            found.data.controlled_list_id,
                            ...itemsToExpandIds,
                        ].map((x) => [x, true]),
                    );
                    selectedKeys.value = { [found.data.id]: true };
                }
                break;
            }
        }
    },
);

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
