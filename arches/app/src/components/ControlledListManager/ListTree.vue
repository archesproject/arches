<script setup lang="ts">
import { inject, ref } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import Tree from "primevue/tree";

import LetterCircle from "@/components/ControlledListManager/LetterCircle.vue";
import ListTreeControls from "@/components/ControlledListManager/ListTreeControls.vue";
import MoveItem from "@/components/ControlledListManager/MoveItem.vue";
import { displayedRowKey, selectedLanguageKey } from "@/components/ControlledListManager/const.ts";
import { bestLabel } from "@/components/ControlledListManager/utils.ts";

import type { Ref } from "@/types/Ref";
import type {
    TreeContext,
    TreeExpandedKeys,
    TreeNode,
    TreeSelectionKeys,
} from "primevue/tree/Tree";

const tree: Ref<typeof TreeNode[]> = ref([]);
const selectedKeys: Ref<typeof TreeSelectionKeys> = ref({});
const expandedKeys: Ref<typeof TreeExpandedKeys> = ref({});

const { setDisplayedRow } = inject(displayedRowKey);
const selectedLanguage = inject(selectedLanguageKey);

const { $gettext } = useGettext();
const modalVisible = ref(false);

const collapseNodesRecursive = (node: typeof TreeNode) => {
    if (node.children && node.children.length) {
        expandedKeys.value = {
            ...expandedKeys.value,
            [node.key]: false,
        };
        for (const child of node.children) {
            collapseNodesRecursive(child);
        }
    }
};

const onRowSelect = (node: typeof TreeNode) => {
    setDisplayedRow(node.data);
    expandedKeys.value = {
        ...expandedKeys.value,
        [node.key]: true,
    };
    if (node.data.name) {
        tree.value.filter(list => list.data.id !== node.data.id)
            .forEach(list => collapseNodesRecursive(list));
    }
};
</script>

<template>
    <ListTreeControls
        v-model="tree"
        v-model:expanded-keys="expandedKeys"
        v-model:selected-keys="selectedKeys"
        :selected-keys
    />
    <Tree
        v-if="tree"
        v-model:selectionKeys="selectedKeys"
        :value="tree"
        :expanded-keys
        :filter="true"
        filter-mode="lenient"
        :filter-placeholder="$gettext('Find')"
        selection-mode="single"
        :pt="{
            root: { style: { flexGrow: 1, border: 0, overflowY: 'hidden' } },
            input: {
                style: { height: '3.5rem', fontSize: '14px' },
            },
            wrapper: { style: { overflowY: 'auto', maxHeight: '100%' } },
            container: { style: { fontSize: '14px' } },
            content: ({ context }) : { context: TreeContext } => ({
                style: { height: '3.5rem' },
            }),
            label: { style: { textWrap: 'nowrap', marginLeft: '0.5rem' } },
        }"
        @node-select="onRowSelect"
    >
        <template #nodeicon="slotProps">
            <LetterCircle :labelled="slotProps.node.data" />
        </template>
        <template #default="slotProps">
            <span class="label-and-actions">
                {{ slotProps.node.data.name ?? bestLabel(slotProps.node.data, selectedLanguage.code).value }}
                <span v-if="!slotProps.node.data.name">
                    <Button
                        v-if="slotProps.node.key in selectedKeys"
                        type="button"
                        class="move-button"
                        :label="$gettext('Move')"
                        @click="modalVisible = true"
                    />
                    <MoveItem
                        v-model="modalVisible"
                        :itemData="slotProps.node.data"
                    />
                </span>
            </span>
        </template>
    </Tree>
</template>

<style scoped>
a {
    color: var(--blue-500);
    font-size: 1.3rem; /* same as arches.scss selected */
}
.label-and-actions {
    display: inline-flex;
    align-items: center;
    gap: 1rem;
}
.move-button {
    background-color: aliceblue;
    color: black;
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
}
</style>
