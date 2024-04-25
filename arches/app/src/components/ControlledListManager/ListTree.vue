<script setup lang="ts">
import arches from "arches";
import Cookies from "js-cookie";
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
    itemAsNode,
    listAsNode,
    reorderItem,
} from "@/components/ControlledListManager/utils.ts";

import type { Ref } from "@/types/Ref";
import type {
    TreeExpandedKeys,
    TreeSelectionKeys,
} from "primevue/tree/Tree";
import type { TreeNode } from "primevue/tree/Tree/TreeNode";
import type {
    ControlledList,
    ControlledListItem,
    NewItem,
} from "@/types/ControlledListManager";

const tree: Ref<typeof TreeNode[]> = ref([]);
const selectedKeys: Ref<TreeSelectionKeys> = ref({});
const expandedKeys: Ref<TreeExpandedKeys> = ref({});
const movingItem: Ref<typeof TreeNode> = ref({});
const isMultiSelecting = ref(false);
const refetcher = ref(0);

const { setDisplayedRow } = inject(displayedRowKey);
const selectedLanguage = inject(selectedLanguageKey);

const toast = useToast();
const { $gettext } = useGettext();
const ERROR = "error";  // not user-facing

const showMoveHereButton = (rowId: string) => {
    return (
        movingItem.value.key
        && rowId in selectedKeys.value
        && rowId !== movingItem.value.key
        && rowId !== movingItem.value.data.parent_id
        && rowId !== movingItem.value.data.controlled_list_id
    );
};

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

const addChild = async (parent_id: string) => {
    let errorText;
    const newItem: NewItem = { parent_id };
    try {
        const response = await fetch(arches.urls.controlled_list_item_add, {
            method: "POST",
            headers: {
                "X-CSRFToken": Cookies.get("csrftoken"),
            },
            body: JSON.stringify(newItem),
        });
        if (response.ok) {
            const newItem = await response.json();
            const parent = findNodeInTree(tree.value, parent_id);
            parent.children.push(itemAsNode(newItem, selectedLanguage.value));
            if (parent.data.name) {
                // Parent node is a list
                parent.data.items.push(newItem);
            } else {
                // Parent node is an item
                parent.data.children.push(newItem);
            }
            expandedKeys.value = {
                ...expandedKeys.value,
                [parent.key]: true,
            };
        } else {
            errorText = response.statusText;
            const body = await response.json();
            errorText = body.message;
            throw new Error();
        }
    } catch {
        toast.add({
            severity: ERROR,
            summary: errorText || $gettext("Item creation failed"),
        });
    }
};

const setParent = async (parentNode: typeof TreeNode) => {
    let errorText;
    const setListAndSortOrderRecursive = (child: ControlledListItem) => {
        child.controlled_list_id = parentNode.key;
        child.sortorder = -1;  // tells backend to renumber
        child.children.forEach(grandchild => setListAndSortOrderRecursive(grandchild));
    };

    const item = movingItem.value.data;

    if (parentNode.data.name) {
        setListAndSortOrderRecursive(item);
    } else {
        item.parent_id = parentNode.key;
    }

    try {
        const response = await fetch(arches.urls.controlled_list_item(item.id), {
            method: "POST",
            headers: {
                "X-CSRFToken": Cookies.get("csrftoken"),
            },
            body: JSON.stringify(item),
        });
        if (response.ok) {
            movingItem.value = {};
            refetcher.value += 1;
        } else {
            errorText = response.statusText;
            const body = await response.json();
            errorText = body.message;
            throw new Error();
        }
    } catch {
        toast.add({
            severity: ERROR,
            summary: errorText || $gettext("Move failed"),
        });
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
        :selection-mode="isMultiSelecting ? 'multiple' : 'single'"
        :pt="{
            root: { style: { flexGrow: 1, border: 0, overflowY: 'hidden' } },
            input: {
                style: { height: '3.5rem', fontSize: '14px' },
            },
            wrapper: { style: { overflowY: 'auto', maxHeight: '100%' } },
            container: { style: { fontSize: '14px' } },
            content: { style: { height: '4rem' } },
            label: { style: { textWrap: 'nowrap', marginLeft: '0.5rem' } },
        }"
        @node-select="onRowSelect"
    >
        <template #nodeicon="slotProps">
            <LetterCircle :labelled="slotProps.node.data" />
        </template>
        <template #default="slotProps">
            <span
                :class="slotProps.node.key === movingItem.key ? 'is-adjusting-parent' : ''"
            >
                {{ slotProps.node.data.name ?? bestLabel(slotProps.node.data, selectedLanguage.code).value }}
                <div
                    v-if="movingItem.key"
                    class="actions"
                >
                    <!-- disable HTML escaping: RDM Admins are trusted users -->
                    <Button
                        v-if="showMoveHereButton(slotProps.node.key)"
                        type="button"
                        class="move-button"
                        :label="$gettext('Move %{item} here', { item: movingItem.label }, true)"
                        @click="setParent(slotProps.node)"
                    />
                </div>
                <div
                    v-else
                    class="actions"
                >
                    <Button
                        v-if="slotProps.node.key in selectedKeys"
                        type="button"
                        class="add-child-button"
                        icon="fa fa-plus"
                        :aria-label="$gettext('Add child item')"
                        @click="addChild(slotProps.node.key)"
                    />
                    <span
                        v-if="!slotProps.node.data.name"
                        class="reorder-buttons"
                    >
                        <Button
                            v-if="slotProps.node.key in selectedKeys"
                            type="button"
                            class="reorder-button"
                            icon="fa fa-caret-up"
                            :aria-label="$gettext('Move up')"
                            :disabled="isFirstItem(slotProps.node.data)"
                            @click="onReorder(slotProps.node.data, true)"
                        />
                        <Button
                            v-if="slotProps.node.key in selectedKeys"
                            type="button"
                            class="reorder-button"
                            icon="fa fa-caret-down"
                            :aria-label="$gettext('Move down')"
                            :disabled="isLastItem(slotProps.node.data)"
                            @click="onReorder(slotProps.node.data, false)"
                        />
                    </span>
                    <Button
                        v-if="!slotProps.node.data.name && slotProps.node.key in selectedKeys"
                        type="button"
                        icon="fa fa-arrows-alt"
                        :aria-label="$gettext('Change item parent')"
                        @click="movingItem = slotProps.node"
                    />
                </div>
            </span>
        </template>
    </Tree>
</template>

<style scoped>
.actions {
    display: inline-flex;
    align-items: center;
    gap: 1rem;
    margin-left: 1rem;
}
.p-button {
    background-color: aliceblue;
    color: black;
    height: 2rem;
}
.add-child-button {
    width: 2rem;
    border-radius: 50%;
}
.reorder-buttons {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}
.reorder-button {
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
    height: 1.5rem;
}
.move-button {
    height: 2.5rem;
}
.is-adjusting-parent {
    color: red;
}
</style>
