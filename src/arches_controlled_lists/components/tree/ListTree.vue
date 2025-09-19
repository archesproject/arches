<script setup lang="ts">
import { inject, ref, useTemplateRef, watch } from "vue";
import { useRoute } from "vue-router";
import { useGettext } from "vue3-gettext";

import Tree from "primevue/tree";

import { displayedRowKey } from "@/arches_controlled_lists/constants.ts";
import { routeNames } from "@/arches_controlled_lists/routes.ts";
import { findNodeInTree, nodeIsList } from "@/arches_controlled_lists/utils.ts";
import ListTreeControls from "@/arches_controlled_lists/components/tree/ListTreeControls.vue";
import TreeRow from "@/arches_controlled_lists/components/tree/TreeRow.vue";

import type { ComponentPublicInstance, Ref } from "vue";
import type { RouteLocationNormalizedLoadedGeneric } from "vue-router";
import type { TreePassThroughMethodOptions } from "primevue/tree";
import type { TreeExpandedKeys, TreeSelectionKeys } from "primevue/tree";
import type { TreeNode } from "primevue/treenode";
import type {
    ControlledList,
    ControlledListItem,
    RowSetter,
    Value,
} from "@/arches_controlled_lists/types";

const { $gettext } = useGettext();

// Defining these in the parent avoids re-running $gettext in thousands of children.
const moveLabels = Object.freeze({
    addChild: $gettext("Add child item"),
    moveUp: $gettext("Move item up"),
    moveDown: $gettext("Move item down"),
    changeParent: $gettext("Change item parent"),
});
const iconLabels = Object.freeze({
    list: $gettext("List"),
    item: $gettext("Item"),
});

const tree: Ref<TreeNode[]> = ref([]);
const selectedKeys: Ref<TreeSelectionKeys> = ref({});
const expandedKeys: Ref<TreeExpandedKeys> = ref({});
const movingItem: Ref<TreeNode | undefined> = ref();
const shouldCopyChildren = ref(true);
const isMultiSelecting = ref(false);
const refetcher = ref(0);
const filterValue = ref("");
const treeComponent = useTemplateRef<ComponentPublicInstance>("treeComponent");

// For next new item's pref label (input textbox)
const newLabelFormValue = ref("");
const nextNewItem = ref<ControlledListItem>();
// For new list entry (input textbox)
const newListFormValue = ref("");
const nextNewList = ref<ControlledList>();
const rerenderTree = ref(0);
const nextFilterChangeNeedsExpandAll = ref(false);
const expandedKeysSnapshotBeforeSearch = ref<TreeExpandedKeys>({});

const { setDisplayedRow } = inject<{ setDisplayedRow: RowSetter }>(
    displayedRowKey,
)!;

const route = useRoute();

const navigate = (newRoute: RouteLocationNormalizedLoadedGeneric) => {
    switch (newRoute.name) {
        case routeNames.splash:
            setDisplayedRow(null);
            expandedKeys.value = {};
            selectedKeys.value = {};
            break;
        case routeNames.list: {
            if (!tree.value.length) {
                return;
            }
            const list = tree.value.find(
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
        case routeNames.item: {
            if (!tree.value.length) {
                return;
            }
            const { found, path } = findNodeInTree(
                tree.value,
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

// React to route changes.
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

// Navigate on initial load of the tree.
watch(tree, () => navigate(route), { once: true });

const updateSelectedAndExpanded = (node: TreeNode) => {
    if (isMultiSelecting.value || movingItem.value?.key) {
        return;
    }
    setDisplayedRow(node.data);
    expandedKeys.value = {
        ...expandedKeys.value,
        [node.key]: true,
    };
};

const expandAll = () => {
    const newExpandedKeys = {};
    for (const node of tree.value) {
        expandNode(node, newExpandedKeys);
    }
    expandedKeys.value = { ...newExpandedKeys };
};

const expandNode = (node: TreeNode, newExpandedKeys: TreeExpandedKeys) => {
    if (node.children && node.children.length) {
        newExpandedKeys[node.key] = true;

        for (const child of node.children) {
            expandNode(child, newExpandedKeys);
        }
    }
};

const expandPathsToFilterResults = (newFilterValue: string) => {
    // https://github.com/primefaces/primevue/issues/3996
    if (filterValue.value && !newFilterValue) {
        expandedKeys.value = { ...expandedKeysSnapshotBeforeSearch.value };
        expandedKeysSnapshotBeforeSearch.value = {};
        // Rerender to avoid error emitted in PrimeVue tree re: aria-selected.
        rerenderTree.value += 1;
    }
    // Expand all on the first interaction with the filter, or if the user
    // has collapsed a node and changes the filter.
    if (
        (!filterValue.value && newFilterValue) ||
        (nextFilterChangeNeedsExpandAll.value &&
            filterValue.value !== newFilterValue)
    ) {
        expandedKeysSnapshotBeforeSearch.value = { ...expandedKeys.value };
        expandAll();
    }
    nextFilterChangeNeedsExpandAll.value = false;
};

function getInputElement() {
    if (treeComponent.value !== null) {
        return treeComponent.value.$el.ownerDocument.querySelector(
            'input[data-pc-name="pcfilterinput"]',
        ) as HTMLInputElement;
    }
}

const restoreFocusToInput = () => {
    // The current implementation of collapsing all nodes when
    // backspacing out the search value relies on rerendering the
    // <Tree> component. Restore focus to the input element.
    if (rerenderTree.value > 0) {
        const inputEl = getInputElement();
        if (inputEl) {
            inputEl.focus();
        }
    }
};

const snoopOnFilterValue = () => {
    // If we wait to react to the emitted filter event, the templated rows
    // will have already rendered. (<TreeRow> bolds search terms.)
    const inputEl = getInputElement();
    if (inputEl) {
        expandPathsToFilterResults(inputEl.value);
        filterValue.value = inputEl.value;
    }
};

function lazyLabelLookup(node: TreeNode) {
    if (nodeIsList(node)) {
        return node.data.name;
    } else {
        return node.data.values.map((val: Value) => val.value);
    }
}
</script>

<template>
    <ListTreeControls
        :key="refetcher"
        v-model:tree="tree"
        v-model:rerender-tree="rerenderTree"
        v-model:expanded-keys="expandedKeys"
        v-model:selected-keys="selectedKeys"
        v-model:moving-item="movingItem"
        v-model:is-multi-selecting="isMultiSelecting"
        v-model:should-copy-children="shouldCopyChildren"
        v-model:next-new-list="nextNewList"
        v-model:new-list-form-value="newListFormValue"
    />
    <Tree
        v-if="tree"
        ref="treeComponent"
        :key="rerenderTree"
        v-model:selection-keys="selectedKeys"
        v-model:expanded-keys="expandedKeys"
        :value="tree"
        :filter="true"
        :filter-by="lazyLabelLookup"
        filter-mode="lenient"
        :filter-placeholder="$gettext('Find')"
        :selection-mode="isMultiSelecting ? 'checkbox' : 'single'"
        :pt="{
            root: {
                style: {
                    flexGrow: 1,
                    overflowY: 'hidden',
                    paddingBottom: '5rem',
                    paddingRight: '0rem',
                },
            },
            pcFilter: {
                root: {
                    ariaLabel: $gettext('Find'),
                    style: { width: '100%', fontSize: 'small' },
                },
            },
            wrapper: {
                style: {
                    overflowY: 'auto',
                    maxHeight: '100%',
                    paddingBottom: '1rem',
                },
            },
            container: { style: { fontSize: '1.4rem' } },
            nodeContent: ({ instance }: TreePassThroughMethodOptions) => {
                if (instance.$el && instance.node.key === movingItem?.key) {
                    instance.$el.classList.add('is-adjusting-parent');
                }
                return { style: { height: '4rem' } };
            },
            nodeIcon: ({ instance }: TreePassThroughMethodOptions) => {
                return { ariaLabel: instance.node.iconLabel };
            },
            nodeLabel: {
                style: {
                    textWrap: 'nowrap',
                    marginLeft: '0.5rem',
                    width: '100%',
                },
            },
            hooks: {
                onBeforeUpdate: snoopOnFilterValue,
                onMounted: restoreFocusToInput,
            },
        }"
        @node-collapse="nextFilterChangeNeedsExpandAll = true"
        @node-select="updateSelectedAndExpanded"
    >
        <template #default="slotProps">
            <TreeRow
                v-model:tree="tree"
                v-model:expanded-keys="expandedKeys"
                v-model:selected-keys="selectedKeys"
                v-model:moving-item="movingItem"
                v-model:refetcher="refetcher"
                v-model:rerender-tree="rerenderTree"
                v-model:next-new-item="nextNewItem"
                v-model:new-label-form-value="newLabelFormValue"
                v-model:new-list-form-value="newListFormValue"
                v-model:filter-value="filterValue"
                :icon-labels
                :move-labels
                :node="slotProps.node"
                :is-multi-selecting="isMultiSelecting"
                :should-copy-children="shouldCopyChildren"
            />
        </template>
    </Tree>
</template>

<style scoped>
:deep(.is-adjusting-parent) {
    border: dashed;
}

:deep(.p-tree-filter-input) {
    height: 3.5rem;
    font-size: 1.4rem;
    border-radius: 2px;
}

:deep(.p-tree-node) {
    margin-inline-end: 0.5rem;
}
</style>
