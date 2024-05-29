<script setup lang="ts">
import { inject, ref } from "vue";

import Tree from "primevue/tree";

import LetterCircle from "@/components/ControlledListManager/LetterCircle.vue";
import ListTreeControls from "@/components/ControlledListManager/ListTreeControls.vue";
import TreeRow from "@/components/ControlledListManager/TreeRow.vue";

import { displayedRowKey } from "@/components/ControlledListManager/constants.ts";

import type { Ref } from "vue";
import type {
    TreeExpandedKeys,
    TreeSelectionKeys,
} from "primevue/tree/Tree";
import type { TreeNode } from "primevue/treenode";
import type {
    ControlledListItem,
    DisplayedRowRefAndSetter,
    NewControlledListItem,
} from "@/types/ControlledListManager";

const tree: Ref<TreeNode[]> = ref([]);
const selectedKeys: Ref<TreeSelectionKeys> = ref({});
const expandedKeys: Ref<TreeExpandedKeys> = ref({});
const movingItem: Ref<TreeNode> = ref({});
const isMultiSelecting = ref(false);
const refetcher = ref(0);
const filterValue = ref("");

// For next new item's pref label (input textbox)
const newLabelCounter = ref(1000);
const newLabelFormValue = ref('');
const nextNewItem = ref<NewControlledListItem>();

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
    if (
        node.data.name
        || (priorListId && (node.data as ControlledListItem).controlled_list_id !== priorListId)
    ) {
        tree.value.filter(list => list.data.id !== node.data.id)
            .forEach(list => collapseNodesRecursive(list));
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
    />
    <Tree
        v-if="tree"
        v-model:selectionKeys="selectedKeys"
        v-model:expandedKeys="expandedKeys"
        :value="tree"
        :filter="true"
        filter-mode="lenient"
        :filter-placeholder="$gettext('Find')"
        :selection-mode="isMultiSelecting ? 'multiple' : 'single'"
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
            label: { style: { textWrap: 'nowrap', marginLeft: '0.5rem' } },
            hooks: {
                onBeforeUpdate() {
                    // Snoop on the filterValue, because if we wait to react
                    // to the emitted filter event, the templated rows will
                    // have already rendered.
                    // @ts-ignore
                    const maybeValue = $el.ownerDocument.getElementsByClassName('p-tree-filter')[0]?.value;
                    if (maybeValue) {
                        (filterValue as any) = maybeValue;
                    }
                },
            },
        }"
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
                v-model:filter-value="filterValue"
                :node="slotProps.node"
            />
        </template>
    </Tree>
</template>

<style scoped>
:deep(.is-adjusting-parent) {
    border: dashed;
}
</style>