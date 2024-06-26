<script setup lang="ts">
import { computed, inject, ref, watch } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import InputText from "primevue/inputtext";
import ProgressSpinner from "primevue/progressspinner";
import { useToast } from "primevue/usetoast";

import {
    createItem,
    createList,
    patchList,
    upsertValue,
} from "@/components/ControlledListManager/api.ts";
import {
    DEFAULT_ERROR_TOAST_LIFE,
    ERROR,
    displayedRowKey,
    selectedLanguageKey,
} from "@/components/ControlledListManager/constants.ts";
import {
    bestLabel,
    findNodeInTree,
    itemAsNode,
    listAsNode,
    nodeIsList,
    reorderItems,
} from "@/components/ControlledListManager/utils.ts";
import MoveRow from "@/components/ControlledListManager/tree/MoveRow.vue";

import type { Language } from "@/types/arches";
import type { Ref } from "vue";
import type { TreeExpandedKeys, TreeSelectionKeys } from "primevue/tree/Tree";
import type { TreeNode } from "primevue/treenode";
import type {
    ControlledList,
    ControlledListItem,
    DisplayedListItemRefAndSetter,
    MoveLabels,
    NewControlledListItem,
} from "@/types/ControlledListManager";

const toast = useToast();
const { $gettext } = useGettext();

const selectedLanguage = inject(selectedLanguageKey) as Ref<Language>;

const tree = defineModel<TreeNode[]>("tree", { required: true });
const expandedKeys = defineModel<TreeExpandedKeys>("expandedKeys", {
    required: true,
});
const selectedKeys = defineModel<TreeSelectionKeys>("selectedKeys", {
    required: true,
});
const movingItem = defineModel<TreeNode>("movingItem", { required: true });
const refetcher = defineModel<number>("refetcher", { required: true });
const rerenderTree = defineModel<number>("rerenderTree", { required: true });
const nextNewItem = defineModel<NewControlledListItem>("nextNewItem");
const newLabelFormValue = defineModel<string>("newLabelFormValue", {
    required: true,
});
const newListFormValue = defineModel<string>("newListFormValue", {
    required: true,
});
const filterValue = defineModel<string>("filterValue", { required: true });

const { isMultiSelecting, node, moveLabels } = defineProps<{
    isMultiSelecting: boolean;
    moveLabels: MoveLabels;
    node: TreeNode;
}>();
const { setDisplayedRow } = inject(
    displayedRowKey,
) as DisplayedListItemRefAndSetter;

const awaitingMove = ref(false);
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
        return "";
    }
    const unstyledLabel =
        node.data.name ??
        bestLabel(node.data, selectedLanguage.value.code).value;
    if (!filterValue.value) {
        return unstyledLabel;
    }
    const regex = new RegExp(`(${filterValue.value})`, "gi");
    return unstyledLabel.replace(regex, "<b>$1</b>");
});

const showMoveHereButton = (rowId: string) => {
    return (
        movingItem.value.key &&
        rowId in selectedKeys.value &&
        rowId !== movingItem.value.key &&
        rowId !== movingItem.value.data.parent_id &&
        (movingItem.value.data.parent_id ||
            rowId !== movingItem.value.data.list_id)
    );
};

const setParent = async (parentNode: TreeNode) => {
    awaitingMove.value = true;

    const item = movingItem.value.data;

    let list: ControlledList;
    let siblings: ControlledListItem[];
    if (nodeIsList(parentNode)) {
        item.parent_id = null;
        item.list_id = parentNode.key;
        list = parentNode.data;
        siblings = list.items;
        siblings.push(item);
    } else {
        item.parent_id = parentNode.key;
        list = findNodeInTree(tree.value, item.list_id).data;
        siblings = parentNode.data.children;
        siblings.push(item);
    }

    reorderItems(list, item, siblings, false);

    const field = "children";
    try {
        await patchList(list, field);
        // Clear custom classes added in <Tree> pass-through
        rerenderTree.value += 1;
        movingItem.value = {};
        refetcher.value += 1;
    } catch (error) {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("Save failed"),
            detail: error instanceof Error ? error.message : undefined,
        });
    }

    awaitingMove.value = false;
};

const isNewList = (node: TreeNode) => {
    return nodeIsList(node) && typeof node.data.id === "number";
};

const isNewItem = (node: TreeNode) => {
    return !nodeIsList(node) && typeof node.data.id === "number";
};

const acceptNewItemShortcutEntry = async () => {
    let newItem: ControlledListItem;
    try {
        newItem = await createItem(nextNewItem.value);
    } catch (error) {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("Item creation failed"),
            detail: error instanceof Error ? error.message : undefined,
        });
        return;
    }
    const newValue = {
        ...nextNewItem.value!.values[0],
        id: 0,
        item_id: newItem.id,
        value: newLabelFormValue.value.trim(),
    };
    try {
        const newLabel = await upsertValue(newValue);
        newItem.values = [newLabel];
    } catch (error) {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("Value save failed"),
            detail: error instanceof Error ? error.message : undefined,
        });
    }

    const parent = findNodeInTree(
        tree.value,
        newItem.parent_id ?? newItem.list_id,
    );
    parent.children = [
        ...parent.children.filter(
            (child: TreeNode) => typeof child.key === "string",
        ),
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
};

const triggerAcceptNewItemShortcut = () => {
    if (newLabelFormValue.value.trim()) {
        newLabelInputRef.value.$el.blur();
    }
};

const triggerAcceptNewListShortcut = () => {
    if (newListFormValue.value.trim()) {
        newListInputRef.value.$el.blur();
    }
};

const acceptNewListShortcutEntry = async () => {
    try {
        const newList = await createList(newListFormValue.value.trim());
        tree.value = [
            ...tree.value.filter((cList) => typeof cList.data.id === "string"),
            listAsNode(newList),
        ];
        selectedKeys.value = { [newList.id]: true };
        setDisplayedRow(newList);
    } catch (error) {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("List creation failed"),
            detail: error instanceof Error ? error.message : undefined,
        });
    }
};
</script>

<template>
    <span
        v-if="node.key"
        style="display: inline-flex; width: 100%; align-items: center"
    >
        <div v-if="isNewItem(node)">
            <InputText
                ref="newLabelInputRef"
                v-model="newLabelFormValue"
                autofocus
                @blur="acceptNewItemShortcutEntry"
                @keyup.enter="triggerAcceptNewItemShortcut"
            />
        </div>
        <div v-else-if="isNewList(node)">
            <InputText
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
            <ProgressSpinner
                v-if="awaitingMove"
                style="height: 2rem"
            />
            <!-- turn off escaping: vue template sanitizes -->
            <Button
                v-else-if="showMoveHereButton(node.key)"
                type="button"
                raised
                class="move-button"
                :label="
                    $gettext(
                        'Move %{item} here',
                        {
                            item: bestLabel(
                                movingItem.data,
                                selectedLanguage.code,
                            ).value,
                        },
                        true,
                    )
                "
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
    height: 2.5rem;
}
</style>
