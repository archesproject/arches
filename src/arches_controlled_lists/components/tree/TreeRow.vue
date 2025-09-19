<script setup lang="ts">
import { computed, inject, ref, useTemplateRef, watch } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import InputText from "primevue/inputtext";
import ProgressSpinner from "primevue/progressspinner";
import { useToast } from "primevue/usetoast";

import {
    createItem,
    createList,
    patchList,
    copyItem,
    upsertValue,
} from "@/arches_controlled_lists/api.ts";
import {
    CONTRAST,
    DEFAULT_ERROR_TOAST_LIFE,
    ERROR,
    SECONDARY,
    displayedRowKey,
    selectedLanguageKey,
    systemLanguageKey,
} from "@/arches_controlled_lists/constants.ts";
import {
    dataIsNew,
    findNodeInTree,
    getItemLabel,
    itemAsNode,
    listAsNode,
    nodeIsList,
    reorderItems,
    shouldUseContrast,
} from "@/arches_controlled_lists/utils.ts";
import MoveRow from "@/arches_controlled_lists/components/tree/MoveRow.vue";

import type { ComponentPublicInstance, Ref } from "vue";
import type { TreeExpandedKeys, TreeSelectionKeys } from "primevue/tree";
import type { TreeNode } from "primevue/treenode";
import type {
    ControlledList,
    ControlledListItem,
    IconLabels,
    Language,
    MoveLabels,
    NewControlledListItem,
    NewValue,
    RowSetter,
} from "@/arches_controlled_lists/types";

const toast = useToast();
const { $gettext } = useGettext();

const selectedLanguage = inject(selectedLanguageKey) as Ref<Language>;
const systemLanguage = inject(systemLanguageKey) as Language;

const tree = defineModel<TreeNode[]>("tree", { required: true });
const expandedKeys = defineModel<TreeExpandedKeys>("expandedKeys", {
    required: true,
});
const selectedKeys = defineModel<TreeSelectionKeys>("selectedKeys", {
    required: true,
});
const movingItem = defineModel<TreeNode>("movingItem");
const refetcher = defineModel<number>("refetcher", { required: true });
const rerenderTree = defineModel<number>("rerenderTree", { required: true });
const nextNewItem = defineModel<ControlledListItem>("nextNewItem");
const newLabelFormValue = defineModel<string>("newLabelFormValue", {
    required: true,
});
const newListFormValue = defineModel<string>("newListFormValue", {
    required: true,
});
const filterValue = defineModel<string>("filterValue", { required: true });

const { isMultiSelecting, shouldCopyChildren, node, iconLabels, moveLabels } =
    defineProps<{
        shouldCopyChildren: boolean;
        isMultiSelecting: boolean;
        iconLabels: IconLabels;
        moveLabels: MoveLabels;
        node: TreeNode;
    }>();
const { setDisplayedRow }: { setDisplayedRow: RowSetter } =
    inject(displayedRowKey)!;

const awaitingMove = ref(false);
// Workaround for autofocusing the new list/label input boxes
// https://github.com/primefaces/primevue/issues/2397
const newListInput = useTemplateRef<ComponentPublicInstance>("newListInput");
const newLabelInput = useTemplateRef<ComponentPublicInstance>("newLabelInput");
watch(newLabelInput, () => {
    if (newLabelInput.value) {
        newLabelInput.value.$el.focus();
    }
});
watch(newListInput, () => {
    if (newListInput.value) {
        newListInput.value.$el.focus();
    }
});

const unstyledLabel = computed(() => {
    if (!node.data) {
        return "";
    }
    return (
        node.data.name ??
        getItemLabel(
            node.data,
            selectedLanguage.value.code,
            systemLanguage.code,
        ).value
    );
});

const splitFilterValue = computed(() => {
    if (!filterValue.value) {
        return [unstyledLabel.value];
    }
    const regex = new RegExp(`(${filterValue.value})`, "gi");
    return unstyledLabel.value.split(regex);
});

const showMoveHereButton = (rowId: string) => {
    return (
        movingItem.value &&
        rowId in selectedKeys.value &&
        rowId !== movingItem.value.key &&
        rowId !== movingItem.value.data.parent_id &&
        (movingItem.value.data.parent_id ||
            rowId !== movingItem.value.data.list_id)
    );
};

const setParent = async (parentNode: TreeNode) => {
    awaitingMove.value = true;

    if (!movingItem.value) {
        throw new Error();
    }
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
        list = findNodeInTree(tree.value, parentNode.data.list_id).found!.data;
        siblings = parentNode.data.children;
        siblings.push(item);
    }

    reorderItems(list, item, siblings, false);

    const field = "children";
    try {
        await patchList(list, field);
    } catch (error) {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("Save failed"),
            detail: error instanceof Error ? error.message : undefined,
        });
        return;
    }
    awaitingMove.value = false;
    // Clear custom classes added in <Tree> pass-through
    rerenderTree.value += 1;
    movingItem.value = undefined;
    refetcher.value += 1;
};

const copyItemTo = async (parentNode: TreeNode) => {
    let list_id: string;
    let parent_id: string | null;

    if (nodeIsList(parentNode)) {
        list_id = parentNode.key;
        parent_id = null;
    } else {
        list_id = parentNode.data.list_id;
        parent_id = parentNode.key;
    }

    try {
        await copyItem(
            movingItem.value!.data.id,
            parent_id,
            list_id,
            shouldCopyChildren,
        );
    } catch (error) {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("Copy failed"),
            detail: error instanceof Error ? error.message : undefined,
        });
        return;
    }

    awaitingMove.value = false;
    // Clear custom classes added in <Tree> pass-through
    rerenderTree.value += 1;
    movingItem.value = undefined;
    refetcher.value += 1;
};

const isNewList = (node: TreeNode) => {
    return nodeIsList(node) && dataIsNew(node.data);
};

const isNewItem = (node: TreeNode) => {
    return !nodeIsList(node) && dataIsNew(node.data);
};

const acceptNewItemShortcutEntry = async () => {
    let newItem: ControlledListItem;
    try {
        newItem = await createItem({
            ...nextNewItem.value,
            id: null,
        } as NewControlledListItem);
    } catch (error) {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("Item creation failed"),
            detail: error instanceof Error ? error.message : undefined,
        });
        return;
    }
    const newValue: NewValue = {
        ...nextNewItem.value!.values[0],
        id: null,
        list_item_id: newItem.id,
        value: newLabelFormValue.value.trim(),
    };
    let newLabel;
    try {
        newLabel = await upsertValue(newValue);
    } catch (error) {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("Value save failed"),
            detail: error instanceof Error ? error.message : undefined,
        });
        return;
    }
    if (newLabel) {
        newItem.values = [newLabel];
    }

    const parent = findNodeInTree(
        tree.value,
        newItem.parent_id ?? newItem.list_id,
    ).found;
    if (!parent) {
        throw new Error();
    }

    parent.children = [
        ...parent.children!.filter((child: TreeNode) => !dataIsNew(child.data)),
        itemAsNode(newItem, selectedLanguage.value, iconLabels),
    ];
    if (nodeIsList(parent)) {
        parent.data.items.push(newItem);
    } else {
        parent.data.children.push(newItem);
    }

    selectedKeys.value = { [newItem.id]: true };
    setDisplayedRow(newItem);
    newLabelFormValue.value = "";
};

const triggerAcceptNewItemShortcut = () => {
    if (newLabelFormValue.value.trim()) {
        newLabelInput.value!.$el.blur();
    }
};

const triggerAcceptNewListShortcut = () => {
    if (newListFormValue.value.trim()) {
        newListInput.value!.$el.blur();
    }
};

const acceptNewListShortcutEntry = async () => {
    let newList;
    try {
        newList = await createList(newListFormValue.value.trim());
    } catch (error) {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("List creation failed"),
            detail: error instanceof Error ? error.message : undefined,
        });
        return;
    }
    tree.value = [
        ...tree.value.filter((cList) => !dataIsNew(cList.data)),
        listAsNode(newList, selectedLanguage.value, iconLabels),
    ];
    selectedKeys.value = { [newList.id]: true };
    setDisplayedRow(newList);
    newListFormValue.value = "";
};
</script>

<template>
    <span
        v-if="node.key"
        style="display: inline-flex; width: 100%; align-items: center"
    >
        <div v-if="isNewItem(node)">
            <InputText
                ref="newLabelInput"
                v-model="newLabelFormValue"
                autofocus
                @blur="acceptNewItemShortcutEntry"
                @keyup.enter="triggerAcceptNewItemShortcut"
            />
        </div>
        <div v-else-if="isNewList(node)">
            <InputText
                ref="newListInput"
                v-model="newListFormValue"
                autofocus
                @blur="acceptNewListShortcutEntry"
                @keyup.enter="triggerAcceptNewListShortcut"
            />
        </div>
        <span>
            {{ splitFilterValue[0]
            }}<template v-if="splitFilterValue[1]">
                <b>{{ splitFilterValue[1] }}</b
                >{{ splitFilterValue[2] }}
            </template>
        </span>
        <div
            v-if="movingItem"
            class="actions"
        >
            <ProgressSpinner
                v-if="awaitingMove"
                style="height: 2rem"
            />
            <!-- turn off escaping: vue template sanitizes -->
            <div v-else-if="showMoveHereButton(node.key)">
                <Button
                    class="move-target"
                    type="button"
                    :severity="shouldUseContrast() ? CONTRAST : SECONDARY"
                    :label="$gettext('Move here')"
                    @click="setParent(node)"
                />
                <Button
                    class="move-target"
                    type="button"
                    :severity="shouldUseContrast() ? CONTRAST : SECONDARY"
                    :label="$gettext('Copy here')"
                    @click="copyItemTo(node)"
                />
            </div>
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
                :node
                :icon-labels
                :move-labels
            />
        </div>
    </span>
</template>

<style scoped>
.actions {
    display: inline-flex;
    gap: 1rem;
    margin-inline-start: 1rem;
    width: 100%;
    justify-content: space-between;
}

.move-target {
    height: 2.5rem;
    font-size: unset;
    border-radius: 2px;
}

:deep(input) {
    height: 3rem;
    font-size: inherit;
}
</style>
