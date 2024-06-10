<script setup lang="ts">
import arches from "arches";
import Cookies from "js-cookie";
import { computed, inject, ref, watch } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import InputText from "primevue/inputtext";
import { useToast } from "primevue/usetoast";

import MoveRow from "@/components/ControlledListManager/MoveRow.vue";

import { createItem, createList, upsertValue } from "@/components/ControlledListManager/api.ts";
import { DEFAULT_ERROR_TOAST_LIFE, ERROR, displayedRowKey, selectedLanguageKey } from "@/components/ControlledListManager/constants.ts";
import {
    bestLabel,
    findNodeInTree,
    itemAsNode,
    listAsNode,
    nodeIsList,
} from "@/components/ControlledListManager/utils.ts";

import type { Ref } from "vue";
import type {
    TreeExpandedKeys,
    TreeSelectionKeys,
} from "primevue/tree/Tree";
import type { TreeNode } from "primevue/treenode";
import type {
    ControlledListItem,
    DisplayedListItemRefAndSetter,
    MoveLabels,
    NewControlledListItem,
} from "@/types/ControlledListManager";
import type { Language } from "@/types/arches";

const toast = useToast();
const { $gettext } = useGettext();

const selectedLanguage = inject(selectedLanguageKey) as Ref<Language>;

const tree = defineModel<TreeNode[]>("tree", { required: true });
const expandedKeys = defineModel<TreeExpandedKeys>("expandedKeys", { required: true });
const selectedKeys = defineModel<TreeSelectionKeys>("selectedKeys", { required: true });
const movingItem = defineModel<TreeNode>("movingItem", { required: true });
const refetcher = defineModel<number>("refetcher", { required: true });
const nextNewItem = defineModel<NewControlledListItem>("nextNewItem");
const newLabelFormValue = defineModel<string>("newLabelFormValue", { required: true });
const newLabelCounter = defineModel<number>("newLabelCounter", { required: true });
const newListFormValue = defineModel<string>("newListFormValue", { required: true });
const newListCounter = defineModel<number>("newListCounter", { required: true });
const filterValue = defineModel<string>("filterValue", { required: true });

const { isMultiSelecting, node, moveLabels } = defineProps<{
    isMultiSelecting: boolean,
    moveLabels: MoveLabels,
    node: TreeNode,
}>();
const { setDisplayedRow } = inject(displayedRowKey) as DisplayedListItemRefAndSetter;

// Workaround for autofocusing the new list/label input boxes
// https://github.com/primefaces/primevue/issues/2397
const newListInputRef = ref();
const newLabelInputRef = ref();
watch(newLabelInputRef, () => {
    if (newLabelInputRef.value) {
        newLabelInputRef.value.$el.focus();
    }
});
watch(newListInputRef, () => {
    if (newListInputRef.value) {
        newListInputRef.value.$el.focus();
    }
});

const rowLabel = computed(() => {
    if (!node.data) {
        return '';
    }
    const unstyledLabel = node.data.name ?? bestLabel(node.data, selectedLanguage.value.code).value;
    if (!filterValue.value) {
        return unstyledLabel;
    }
    const regex = new RegExp(`(${filterValue.value})`, "gi");
    return unstyledLabel.replace(regex, "<b>$1</b>");
});

const showMoveHereButton = (rowId: string) => {
    return (
        movingItem.value.key
        && rowId in selectedKeys.value
        && rowId !== movingItem.value.key
        && rowId !== movingItem.value.data.parent_id
        && rowId !== movingItem.value.data.controlled_list_id
    );
};

const setParent = async (parentNode: TreeNode) => {
    let error;
    let response;

    const setListAndSortOrderRecursive = (child: ControlledListItem) => {
        if (!parentNode.key) {
            return;
        }
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

    const token = Cookies.get("csrftoken");
    if (!token) {
        return;
    }
    try {
        response = await fetch(arches.urls.controlled_list_item(item.id), {
            method: "POST",
            headers: { "X-CSRFToken": token },
            body: JSON.stringify(item),
        });
        if (response.ok) {
            movingItem.value = {};
            refetcher.value += 1;
        } else {
            error = await response.json();
            throw new Error();
        }
    } catch {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("Move failed"),
            detail: error?.message || response?.statusText,
        });
    }
};

const isNewList = (node: TreeNode) => {
    return nodeIsList(node) && typeof node.data.id === 'number';
};

const isNewItem = (node: TreeNode) => {
    return node.data.values && !node.data.values[0].id;
};

const acceptNewItemShortcutEntry = async () => {
    const newItem = await createItem(nextNewItem.value, toast, $gettext);
    if (newItem) {
        const newValue = {
            ...nextNewItem.value!.values[0],
            id: 0,
            item_id: newItem.id,
            value: newLabelFormValue.value.trim(),
        };
        const newLabel = await upsertValue(newValue, toast, $gettext);

        if (newLabel) {
            newItem.values = [newLabel];
        }

        const parent = findNodeInTree(tree.value, newItem.parent_id ?? newItem.controlled_list_id);
        parent.children = [
            ...parent.children.filter((child: TreeNode) => typeof child.key === 'string'),
            itemAsNode(newItem, selectedLanguage.value),
        ];
        if (parent.data.name) {
            // Parent node is a list
            parent.data.items.push(newItem);
        } else {
            // Parent node is an item
            parent.data.children.push(newItem);
        }

        selectedKeys.value = { [newItem.id]: true };
        setDisplayedRow(newItem);
    }
};

const triggerAcceptNewItemShortcut = () => {
    newLabelInputRef.value.$el.blur();
};

const triggerAcceptNewListShortcut = () => {
    newLabelInputRef.value.$el.blur();
};

const acceptNewListShortcutEntry = async () => {
    const newList = await createList(newListFormValue.value.trim(), toast, $gettext);
    tree.value = [
        ...tree.value.filter(lst => typeof lst.data.id === 'string'),
        listAsNode(newList),
    ];
    selectedKeys.value = { [newList.id]: true };
    setDisplayedRow(newList);
};
</script>

<template>
    <span
        v-if="node.key"
        style="display: inline-flex; width: 100%;"
    >
        <div v-if="isNewItem(node)">
            <InputText
                :key="newLabelCounter"
                ref="newLabelInputRef"
                v-model="newLabelFormValue"
                autofocus
                @blur="acceptNewItemShortcutEntry"
                @keyup.enter="triggerAcceptNewItemShortcut"
            />
        </div>
        <div v-else-if="isNewList(node)">
            <InputText
                :key="newListCounter"
                ref="newListInputRef"
                v-model="newListFormValue"
                autofocus
                @blur="acceptNewListShortcutEntry"
                @keyup.enter="triggerAcceptNewListShortcut"
            />
        </div>
        <!-- eslint-disable vue/no-v-html -->
        <span
            v-else
            v-html="rowLabel"
        />
        <!-- eslint-enable vue/no-v-html -->
        <div
            v-if="movingItem.key"
            class="actions"
        >
            <!-- turn off escaping: vue template sanitizes -->
            <Button
                v-if="showMoveHereButton(node.key)"
                type="button"
                raised
                class="move-button"
                :label="$gettext('Move %{item} here', {
                    item: bestLabel(movingItem.data, selectedLanguage.code).value
                }, true)"
                @click="setParent(node)"
            />
        </div>
        <div
            v-else-if="!isNewList(node) && !isNewItem(node)"
            class="actions"
        >
            <MoveRow
                v-if="!isMultiSelecting"
                v-model:tree="tree"
                v-model:expanded-keys="expandedKeys"
                v-model:selected-keys="selectedKeys"
                v-model:moving-item="movingItem"
                v-model:next-new-item="nextNewItem"
                v-model:new-label-form-value="newLabelFormValue"
                v-model:new-label-counter="newLabelCounter"
                :node
                :move-labels
            />
        </div>
    </span>
</template>

<style scoped>
.actions {
    display: inline-flex;
    gap: 1rem;
    margin-left: 1rem;
    width: 100%;
    justify-content: space-between;
}
.p-button {
    background-color: aliceblue;
    color: black;
    height: 2rem;
}
</style>
