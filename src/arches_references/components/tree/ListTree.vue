<script setup lang="ts">
import { computed, inject, ref } from "vue";
import { useGettext } from "vue3-gettext";

import Tree from "primevue/tree";

import {
    displayedRowKey,
    selectedLanguageKey,
} from "@/arches_references/constants.ts";
import { bestLabel, nodeIsList } from "@/arches_references/utils.ts";
import LetterCircle from "@/arches_references/components/misc/LetterCircle.vue";
import ListTreeControls from "@/arches_references/components/tree/ListTreeControls.vue";
import TreeRow from "@/arches_references/components/tree/TreeRow.vue";

import type { ComponentPublicInstance, Ref } from "vue";
import type { TreePassThroughMethodOptions } from "primevue/tree";
import type { TreeExpandedKeys, TreeSelectionKeys } from "primevue/tree";
import type { TreeNode } from "primevue/treenode";
import type { Language } from "@/arches/types";
import type {
    ControlledList,
    ControlledListItem,
    RowSetter,
} from "@/arches_references/types";

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
const movingItem: Ref<TreeNode | undefined> = ref();
const isMultiSelecting = ref(false);
const refetcher = ref(0);
const filterValue = ref("");
const treeDOMRef: Ref<ComponentPublicInstance | null> = ref(null);

// For next new item's pref label (input textbox)
const newLabelFormValue = ref("");
const nextNewItem = ref<ControlledListItem>();
// For new list entry (input textbox)
const newListFormValue = ref("");
const nextNewList = ref<ControlledList>();
const rerenderTree = ref(0);
const nextFilterChangeNeedsExpandAll = ref(false);
const expandedKeysSnapshotBeforeSearch = ref<TreeExpandedKeys>({});

const selectedLanguage = inject(selectedLanguageKey) as Ref<Language>;
const { setDisplayedRow } = inject(displayedRowKey) as unknown as {
    setDisplayedRow: RowSetter;
};

const updateSelectedAndExpanded = (node: TreeNode) => {
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

const getInputElement = () => {
    if (treeDOMRef.value !== null) {
        return treeDOMRef.value.$el.ownerDocument.getElementsByClassName(
            "p-tree-filter-input",
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

// Factored out because of vue-tsc problems inside the pt object
const ptNodeContent = ({ instance }: TreePassThroughMethodOptions) => {
    if (instance.$el && instance.node.key === movingItem.value?.key) {
        instance.$el.classList.add("is-adjusting-parent");
    }
    return { style: { height: "4rem" } };
};
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
                    overflowY: 'hidden',
                    paddingBottom: '5rem',
                },
            },
            pcFilter: {
                root: {
                    ariaLabel: $gettext('Find'),
                    style: { width: '100%', fontSize: 'small' },
                },
            },
            filterIcon: { style: { display: 'flex' } },
            wrapper: {
                style: {
                    overflowY: 'auto',
                    maxHeight: '100%',
                    paddingBottom: '1rem',
                },
            },
            container: { style: { fontSize: '1.4rem' } },
            nodeContent: ptNodeContent,
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

:deep(.p-tree-filter-input) {
    height: 3.5rem;
    font-size: 1.4rem;
}
</style>
