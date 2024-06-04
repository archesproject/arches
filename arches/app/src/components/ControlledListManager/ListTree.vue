<script setup lang="ts">
import { inject, ref } from "vue";
import { useGettext } from "vue3-gettext";

import Tree from "primevue/tree";

import LetterCircle from "@/components/ControlledListManager/LetterCircle.vue";
import ListTreeControls from "@/components/ControlledListManager/ListTreeControls.vue";
import TreeRow from "@/components/ControlledListManager/TreeRow.vue";

import { displayedRowKey } from "@/components/ControlledListManager/constants.ts";
import { nodeIsList } from "@/components/ControlledListManager/utils.ts";

import type { ComponentPublicInstance, Ref } from "vue";
import type {
    TreeExpandedKeys,
    TreeSelectionKeys,
} from "primevue/tree/Tree";
import type { TreeNode } from "primevue/treenode";
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
const newLabelCounter = ref(1000);
const newLabelFormValue = ref('');
const nextNewItem = ref<NewControlledListItem>();
// For new list entry (input textbox)
const newListCounter = ref(1000);
const newListFormValue = ref('');
const nextNewList = ref<NewControlledList>();
// For rerendering tree to avoid error emitted in PrimeVue tree re: aria-selected
const rerender = ref(0);
const nextFilterChangeNeedsExpandAll = ref(false);

const { displayedRow, setDisplayedRow } = inject(displayedRowKey) as DisplayedRowRefAndSetter;

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

const onRowSelect = (node: TreeNode) => {
    let priorListId;
    if (displayedRow.value) {
        priorListId = (displayedRow.value as ControlledListItem).controlled_list_id ?? displayedRow.value.id;
    }

    setDisplayedRow(node.data);
    expandedKeys.value = {
        ...expandedKeys.value,
        [node.key as string]: true,
    };
    if (nodeIsList(node)) {
        tree.value.filter(list => list.data.id !== node.data.id)
            .forEach(list => collapseNodesRecursive(list));
    } else if ((node.data as ControlledListItem).controlled_list_id !== priorListId) {
        tree.value.filter(list => list.data.id !== node.data.controlled_list_id)
            .forEach(list => collapseNodesRecursive(list));
    }
};

const collapseAll = () => {
    expandedKeys.value = {};
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
        collapseAll();
        // Rerender to avoid error emitted in PrimeVue tree re: aria-selected.
        rerender.value += 1;
    }
    // Expand all on the first interaction with the filter, or if the user
    // has collapsed a node and changes the filter.
    if (
        (!filterValue.value && newFilterValue)
        || (nextFilterChangeNeedsExpandAll.value && (filterValue.value !== newFilterValue))
    ) {
        expandAll();
    }
    nextFilterChangeNeedsExpandAll.value = false;
};

const onBeforeUpdate = () => {
    // Snoop on the filterValue, because if we wait to react
    // to the emitted filter event, the templated rows will
    // have already rendered. (<TreeRow> bolds search terms.)
    if (treeDOMRef.value !== null) {
        const inputEl = treeDOMRef.value.$el.ownerDocument
            .getElementsByClassName('p-tree-filter')[0] as HTMLInputElement;

        expandPathsToFilterResults(inputEl.value);
        filterValue.value = inputEl.value;
    }
};
</script>

<template>
    <ListTreeControls
        :key="refetcher"
        v-model="tree"
        v-model:expanded-keys="expandedKeys"
        v-model:selected-keys="selectedKeys"
        v-model:moving-item="movingItem"
        v-model:is-multi-selecting="isMultiSelecting"
        v-model:nextNewList="nextNewList"
        v-model:newListCounter="newListCounter"
        v-model:newListFormValue="newListFormValue"
    />
    <Tree
        v-if="tree"
        ref="treeDOMRef"
        :key="rerender"
        v-model:selectionKeys="selectedKeys"
        v-model:expandedKeys="expandedKeys"
        :value="tree"
        :filter="true"
        filter-mode="lenient"
        :filter-placeholder="$gettext('Find')"
        :selection-mode="isMultiSelecting ? 'checkbox' : 'single'"
        :pt="{
            root: { style: { flexGrow: 1, border: 0, overflowY: 'hidden' } },
            input: {
                style: { height: '3.5rem', fontSize: '14px' },
            },
            wrapper: { style: { overflowY: 'auto', maxHeight: '100%', paddingBottom: '1rem' } },
            container: { style: { fontSize: '14px' } },
            content: ({ instance }) => {
                if (instance.$el && instance.node.key === movingItem.key) {
                    instance.$el.classList.add('is-adjusting-parent');
                }
                return { style: { height: '4rem' } };
            },
            label: { style: { textWrap: 'nowrap', marginLeft: '0.5rem', width: '100%' } },
            hooks: { onBeforeUpdate },
        }"
        @node-collapse="nextFilterChangeNeedsExpandAll = true"
        @node-select="onRowSelect"
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
                v-model:nextNewItem="nextNewItem"
                v-model:newLabelCounter="newLabelCounter"
                v-model:newLabelFormValue="newLabelFormValue"
                v-model:newListCounter="newListCounter"
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