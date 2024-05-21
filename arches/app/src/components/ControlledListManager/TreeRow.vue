<script setup lang="ts">
import arches from "arches";
import Cookies from "js-cookie";
import { computed, inject } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import { useToast } from "primevue/usetoast";

import { postListToServer } from "@/components/ControlledListManager/api.ts";
import { ERROR, selectedLanguageKey } from "@/components/ControlledListManager/constants.ts";
import {
    bestLabel,
    findNodeInTree,
    itemAsNode,
    listAsNode,
    reorderItem,
} from "@/components/ControlledListManager/utils.ts";

import type { Ref } from "vue";
import type {
    TreeExpandedKeys,
    TreeSelectionKeys,
} from "primevue/tree/Tree";
import type { TreeNode } from "primevue/treenode";
import type {
    ControlledList,
    ControlledListItem,
    NewItem,
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

const { node } = defineProps<{ node: TreeNode }>();

const rowLabel = computed(() => {
    if (!node.data) {
        return '';
    }
    return node.data.name ?? bestLabel(node.data, selectedLanguage.value.code).value;
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
    let errorText;
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
        const response = await fetch(arches.urls.controlled_list_item(item.id), {
            method: "POST",
            headers: { "X-CSRFToken": token },
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

const addChild = async (parent_id: string) => {
    let errorText;
    const newItem: NewItem = { parent_id };
    const token = Cookies.get("csrftoken");
    if (!token) {
        return;
    }
    try {
        const response = await fetch(arches.urls.controlled_list_item_add, {
            method: "POST",
            headers: { "X-CSRFToken": token },
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

const onReorder = async (item: ControlledListItem, up: boolean) => {
    const list: ControlledList = findNodeInTree(tree.value, item.controlled_list_id).data;
    const siblings: ControlledListItem[] = (
        item.parent_id
        ? findNodeInTree(tree.value, item.parent_id).children.map(
            (child: TreeNode) => child.data)
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
    const siblings: TreeNode[] = (
        item.parent_id
        ? findNodeInTree(tree.value, item.parent_id).data.children
        : findNodeInTree(tree.value, item.controlled_list_id).data.items
    );
    if (!siblings) {
        throw new Error();
    }
    return siblings[0].id === item.id;
};

const isLastItem = (item: ControlledListItem) => {
    const siblings: TreeNode[] = (
        item.parent_id
        ? findNodeInTree(tree.value, item.parent_id).data.children
        : findNodeInTree(tree.value, item.controlled_list_id).data.items
    );
    if (!siblings) {
        throw new Error();
    }
    return siblings[siblings.length - 1].id === item.id;
};
</script>

<template>
    <span
        v-if="node.key"
        :class="node.key === movingItem.key ? 'is-adjusting-parent' : ''"
    >
        {{ rowLabel }}
        <div
            v-if="movingItem.key"
            class="actions"
        >
            <!-- turn off escaping: vue template sanitizes -->
            <Button
                v-if="showMoveHereButton(node.key)"
                type="button"
                class="move-button"
                :label="$gettext('Move %{item} here', { item: movingItem.label ?? '' }, true)"
                @click="setParent(node)"
            />
        </div>
        <div
            v-else
            class="actions"
        >
            <Button
                v-if="node.key in selectedKeys"
                type="button"
                class="add-child-button"
                icon="fa fa-plus"
                :aria-label="$gettext('Add child item')"
                @click="addChild(node.key)"
            />
            <span
                v-if="!node.data.name"
                class="reorder-buttons"
            >
                <Button
                    v-if="node.key in selectedKeys"
                    type="button"
                    class="reorder-button"
                    icon="fa fa-caret-up"
                    :aria-label="$gettext('Move up')"
                    :disabled="isFirstItem(node.data)"
                    @click="onReorder(node.data, true)"
                />
                <Button
                    v-if="node.key in selectedKeys"
                    type="button"
                    class="reorder-button"
                    icon="fa fa-caret-down"
                    :aria-label="$gettext('Move down')"
                    :disabled="isLastItem(node.data)"
                    @click="onReorder(node.data, false)"
                />
            </span>
            <Button
                v-if="!node.data.name && node.key in selectedKeys"
                type="button"
                icon="fa fa-arrows-alt"
                :aria-label="$gettext('Change item parent')"
                @click="movingItem = node"
            />
        </div>
    </span>
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
