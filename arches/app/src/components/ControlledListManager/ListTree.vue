<script setup lang="ts">
import { inject, ref } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import Tree from "primevue/tree";
import { useToast } from "primevue/usetoast";

import LetterCircle from "@/components/ControlledListManager/LetterCircle.vue";
import ListTreeControls from "@/components/ControlledListManager/ListTreeControls.vue";
import { displayedRowKey, selectedLanguageKey } from "@/components/ControlledListManager/const.ts";
import { postListToServer } from "@/components/ControlledListManager/api.ts";
import {
    bestLabel,
    findNodeInTree,
    listAsNode,
    reorderItem,
} from "@/components/ControlledListManager/utils.ts";

import type { Ref } from "@/types/Ref";
import type {
    TreeContext,
    TreeExpandedKeys,
    TreeNode,
    TreeSelectionKeys,
} from "primevue/tree/Tree";
import type {
    ControlledList,
    ControlledListItem,
} from "@/types/ControlledListManager";

const tree: Ref<typeof TreeNode[]> = ref([]);
const selectedKeys: Ref<typeof TreeSelectionKeys> = ref({});
const expandedKeys: Ref<typeof TreeExpandedKeys> = ref({});

const { setDisplayedRow } = inject(displayedRowKey);
const selectedLanguage = inject(selectedLanguageKey);

const toast = useToast();
const { $gettext } = useGettext();

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

const onReorder = async (item: ControlledListItem, up: boolean) => {
    const list: ControlledList = findNodeInTree(tree.value, item.controlled_list_id).data;
    const siblings: ControlledListItem[] = (
        item.parent_id
        ? findNodeInTree(tree.value, item.parent_id).children.map(
            (child: typeof TreeNode) => child.data)
        : list.items
    );

    reorderItem(list, item, siblings, up);

    const newList = await postListToServer(list, toast, $gettext);
    if (newList) {
        const oldListIndex = tree.value.findIndex(listNode => listNode.data.id === list.id);
        tree.value = [
            ...tree.value.slice(0, oldListIndex),
            listAsNode(newList, selectedLanguage.value),
            ...tree.value.slice(oldListIndex + 1),
        ];
        selectedKeys.value = {
            ...selectedKeys.value,
            [item.id]: true,
        };
    }
};

const isFirstItem = (item: ControlledListItem) => {
    const siblings: typeof TreeNode[] = (
        item.parent_id
        ? findNodeInTree(tree.value, item.parent_id).data.children
        : findNodeInTree(tree.value, item.controlled_list_id).data.items
    );
    if (!siblings) {
        throw new Error("Unexpected lack of siblings");
    }
    return siblings[0].id === item.id;
};


const isLastItem = (item: ControlledListItem) => {
    const siblings: typeof TreeNode[] = (
        item.parent_id
        ? findNodeInTree(tree.value, item.parent_id).data.children
        : findNodeInTree(tree.value, item.controlled_list_id).data.items
    );
    if (!siblings) {
        throw new Error("Unexpected lack of siblings");
    }
    return siblings[siblings.length - 1].id === item.id;
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
                style: { height: '4rem' },
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
                <span
                    v-if="!slotProps.node.data.name"
                    class="move-buttons"
                >
                    <Button
                        v-if="slotProps.node.key in selectedKeys"
                        type="button"
                        class="move-button"
                        icon="fa fa-caret-up"
                        :aria-label="$gettext('Move up')"
                        :disabled="isFirstItem(slotProps.node.data)"
                        @click="onReorder(slotProps.node.data, true)"
                    />
                    <Button
                        v-if="slotProps.node.key in selectedKeys"
                        type="button"
                        class="move-button"
                        icon="fa fa-caret-down"
                        :aria-label="$gettext('Move down')"
                        :disabled="isLastItem(slotProps.node.data)"
                        @click="onReorder(slotProps.node.data, false)"
                    />
                </span>
            </span>
        </template>
    </Tree>
</template>

<style scoped>
.label-and-actions {
    display: inline-flex;
    align-items: center;
    gap: 1rem;
}
.move-buttons {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}
.move-button {
    background-color: aliceblue;
    color: black;
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
    height: 1.5rem;
}
</style>
