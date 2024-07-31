<script setup lang="ts">
import { inject, watch } from "vue";
import { useRoute } from "vue-router";

import { displayedRowKey, routes } from "@/arches_references/constants.ts";
import { findNodeInTree } from "@/arches_references/utils.ts";
import ActionBanner from "@/arches_references/components/tree/ActionBanner.vue";
import AddDeleteControls from "@/arches_references/components/tree/AddDeleteControls.vue";
import PresentationControls from "@/arches_references/components/tree/PresentationControls.vue";

import type { RouteLocationNormalizedLoadedGeneric } from "vue-router";
import type { TreeExpandedKeys, TreeSelectionKeys } from "primevue/tree";
import type { TreeNode } from "primevue/treenode";
import type { ControlledList, RowSetter } from "@/arches_references/types";

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
const nextNewList = defineModel<ControlledList>("nextNewList");
const newListFormValue = defineModel<string>("newListFormValue", {
    required: true,
});

const { setDisplayedRow } = inject(displayedRowKey) as unknown as {
    setDisplayedRow: RowSetter;
};
const route = useRoute();
watch(
    [
        () => {
            return { ...route };
        },
    ],
    ([newRoute]) => {
        navigate(newRoute);
    },
);
const navigate = (newRoute: RouteLocationNormalizedLoadedGeneric) => {
    switch (newRoute.name) {
        case routes.splash:
            setDisplayedRow(null);
            expandedKeys.value = {};
            selectedKeys.value = {};
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
                expandedKeys.value = {
                    ...expandedKeys.value,
                    [list.data.id]: true,
                };
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
                newRoute.params.id as string,
            );
            if (found) {
                setDisplayedRow(found.data);
                const itemsToExpandIds = path.map(
                    (itemInPath: TreeNode) => itemInPath.key,
                );
                expandedKeys.value = {
                    ...expandedKeys.value,
                    ...Object.fromEntries(
                        [
                            found.data.controlled_list_id,
                            ...itemsToExpandIds,
                        ].map((x) => [x, true]),
                    ),
                };
                selectedKeys.value = { [found.data.id]: true };
            }
            break;
        }
    }
};

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

// Navigate on initial load of the tree.
watch(
    controlledListItemsTree,
    () => {
        navigate(route);
    },
    { once: true },
);
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
    background: var(--p-primary-50);
    gap: 0.5rem;
    padding: 0.5rem;
    justify-content: space-between;
}
</style>
