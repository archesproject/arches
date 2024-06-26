<script setup lang="ts">
import { computed, inject, ref } from "vue";
import { useGettext } from "vue3-gettext";

import Tree from "primevue/tree";

import {
    displayedRowKey,
    selectedLanguageKey,
} from "@/components/ControlledListManager/constants.ts";
import {
    bestLabel,
    nodeIsList,
} from "@/components/ControlledListManager/utils.ts";
import LetterCircle from "@/components/ControlledListManager/misc/LetterCircle.vue";
import ListTreeControls from "@/components/ControlledListManager/tree/ListTreeControls.vue";
import TreeRow from "@/components/ControlledListManager/tree/TreeRow.vue";

import type { ComponentPublicInstance, Ref } from "vue";
import type { TreeExpandedKeys, TreeSelectionKeys } from "primevue/tree/Tree";
import type { TreeNode } from "primevue/treenode";
import type { Language } from "@/types/arches";
import type {
    ControlledListItem,
    DisplayedRowRefAndSetter,
    NewControlledList,
    NewControlledListItem,
} from "@/types/ControlledListManager";

const { $gettext } = useGettext();

const moveLabels = Object.freeze({
    addChild: $gettext("Add child item"),
    moveUp: $gettext("Move item up"),
    moveDown: $gettext("Move item down"),
    changeParent: $gettext("Change item parent"),
});

const tree: Ref<TreeNode[]> = ref([]);
const selectedKeys: Ref<TreeSelectionKeys> = ref({});
const expandedKeys: Ref<TreeExpandedKeys> = ref({});
const movingItem: Ref<TreeNode> = ref({});
const isMultiSelecting = ref(false);
const refetcher = ref(0);
const filterValue = ref("");
const treeDOMRef: Ref<ComponentPublicInstance | null> = ref(null);

// For next new item's pref label (input textbox)
const newLabelFormValue = ref("");
const nextNewItem = ref<NewControlledListItem>();
// For new list entry (input textbox)
const newListFormValue = ref("");
const nextNewList = ref<NewControlledList>();
const rerenderTree = ref(0);
const nextFilterChangeNeedsExpandAll = ref(false);

const selectedLanguage = inject(selectedLanguageKey) as Ref<Language>;
const { displayedRow, setDisplayedRow } = inject(
    displayedRowKey,
) as DisplayedRowRefAndSetter;

const collapseNodesRecursive = (node: TreeNode) => {
    if (node.children && node.children.length) {
        expandedKeys.value = {
            ...expandedKeys.value,
            [node.key as string]: false,
        };
        for (const child of node.children) {
            collapseNodesRecursive(child);
        }
    }
};

const updateSelectedAndExpanded = (node: TreeNode) => {
    let priorListId;
    if (displayedRow.value) {
        priorListId =
            (displayedRow.value as ControlledListItem).list_id ??
            displayedRow.value.id;
    }

    setDisplayedRow(node.data);
    expandedKeys.value = {
        ...expandedKeys.value,
        [node.key as string]: true,
    };
    if (nodeIsList(node)) {
        tree.value
            .filter((list) => list.data.id !== node.data.id)
            .forEach((list) => collapseNodesRecursive(list));
    } else if ((node.data as ControlledListItem).list_id !== priorListId) {
        tree.value
            .filter((list) => list.data.id !== node.data.list_id)
            .forEach((list) => collapseNodesRecursive(list));
    }
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
        newExpandedKeys[node.key as string] = true;

        for (const child of node.children) {
            expandNode(child, newExpandedKeys);
        }
    }
};

const expandPathsToFilterResults = (newFilterValue: string) => {
    // https://github.com/primefaces/primevue/issues/3996
    if (filterValue.value && !newFilterValue) {
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
        expandAll();
    }
    nextFilterChangeNeedsExpandAll.value = false;
};

const getInputElement = () => {
    if (treeDOMRef.value !== null) {
        return treeDOMRef.value.$el.ownerDocument.getElementsByClassName(
            "p-tree-filter",
        )[0] as HTMLInputElement;
    }
};

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

const filterCallbackWrapped = computed(() => {
    // Access some hidden functionality of the PrimeVue <Tree> to make
    // filter lookups lazy, that is, making use of the current state of the
    // label values and the selected language when doing the filtering.
    // "Hidden", because we need to violate the type of filter-by, which
    // should be a string. If we abuse it to be something that returns
    // a 1-element array containing a getter when split() is called on it,
    // that getter can return the best label to filter against.
    return {
        split: () => {
            return [
                (node: TreeNode) => {
                    if (nodeIsList(node)) {
                        return node.data.name;
                    }
                    return bestLabel(node.data, selectedLanguage.value.code)
                        .value;
                },
            ];
        },
    };
});
</script>

<template>
    <ListTreeControls
        :key="refetcher"
        v-model="tree"
        v-model:rerender-tree="rerenderTree"
        v-model:expanded-keys="expandedKeys"
        v-model:selected-keys="selectedKeys"
        v-model:moving-item="movingItem"
        v-model:is-multi-selecting="isMultiSelecting"
        v-model:nextNewList="nextNewList"
        v-model:newListFormValue="newListFormValue"
    />
    <Tree
        v-if="tree"
        ref="treeDOMRef"
        :key="rerenderTree"
        v-model:selectionKeys="selectedKeys"
        v-model:expandedKeys="expandedKeys"
        :value="tree"
        :filter="true"
        :filter-by="filterCallbackWrapped as unknown as string"
        filter-mode="lenient"
        :filter-placeholder="$gettext('Find')"
        :selection-mode="isMultiSelecting ? 'checkbox' : 'single'"
        :pt="{
            root: {
                style: {
                    flexGrow: 1,
                    border: 0,
                    overflowY: 'hidden',
                    paddingBottom: '5rem',
                },
            },
            input: {
                style: { height: '3.5rem', fontSize: '1.4rem' },
                ariaLabel: $gettext('Find'),
            },
            wrapper: {
                style: {
                    overflowY: 'auto',
                    maxHeight: '100%',
                    paddingBottom: '1rem',
                },
            },
            container: { style: { fontSize: '1.4rem' } },
            content: ({ instance }) => {
                if (instance.$el && instance.node.key === movingItem.key) {
                    instance.$el.classList.add('is-adjusting-parent');
                }
                return { style: { height: '4rem' } };
            },
            label: {
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
        <template #nodeicon="slotProps">
            <LetterCircle :labelled="slotProps.node.data" />
        </template>
        <template #default="slotProps">
            <TreeRow
                v-model:tree="tree"
                v-model:expanded-keys="expandedKeys"
                v-model:selected-keys="selectedKeys"
                v-model:moving-item="movingItem"
                v-model:refetcher="refetcher"
                v-model:rerenderTree="rerenderTree"
                v-model:nextNewItem="nextNewItem"
                v-model:newLabelFormValue="newLabelFormValue"
                v-model:newListFormValue="newListFormValue"
                v-model:filter-value="filterValue"
                :move-labels
                :node="slotProps.node"
                :is-multi-selecting="isMultiSelecting"
            />
        </template>
    </Tree>
</template>

<style scoped>
:deep(.is-adjusting-parent) {
    border: dashed;
}
</style>
