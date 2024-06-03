<script setup lang="ts">
import arches from "arches";
import { inject } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import { useToast } from "primevue/usetoast";

import { patchList } from "@/components/ControlledListManager/api.ts";
import { PREF_LABEL, displayedRowKey, selectedLanguageKey } from "@/components/ControlledListManager/constants.ts";
import {
    findNodeInTree,
    itemAsNode,
    listAsNode,
    nodeIsList,
    reorderItems,
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
    DisplayedListItemRefAndSetter,
    NewControlledListItem,
} from "@/types/ControlledListManager";
import type { Language } from "@/types/arches";

const toast = useToast();
const { $gettext } = useGettext();

const selectedLanguage = inject(selectedLanguageKey) as Ref<Language>;
const { displayedRow, setDisplayedRow } = inject(displayedRowKey) as DisplayedListItemRefAndSetter;

const { node } = defineProps<{ node: TreeNode }>();

const tree = defineModel<TreeNode[]>("tree", { required: true });
const expandedKeys = defineModel<TreeExpandedKeys>("expandedKeys", { required: true });
const selectedKeys = defineModel<TreeSelectionKeys>("selectedKeys", { required: true });
const movingItem = defineModel<TreeNode>("movingItem", { required: true });
const nextNewItem = defineModel<NewControlledListItem>("nextNewItem");
const newLabelFormValue = defineModel<string>("newLabelFormValue", { required: true });
const newLabelCounter = defineModel<number>("newLabelCounter", { required: true });

const addChildItemLabel = $gettext("Add child item");
const moveUpLabel = $gettext("Move item up");
const moveDownLabel = $gettext("Move item down");
const changeParentLabel = $gettext("Change item parent");


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

const setMovingItem = (node: TreeNode) => {
    movingItem.value = findNodeInTree(
        [itemAsNode(displayedRow.value, selectedLanguage.value)],
        node.key
    );
};

const onAddItem = (parent: TreeNode) => {
    const newItem: NewControlledListItem = {
        parent_id: parent.key!,
        id: newLabelCounter.value,
        controlled_list_id: parent.controlled_list_id ?? parent.id,
        uri: '',
        sortorder: 0,
        guide: false,
        values: [{
            id: 0,
            valuetype_id: PREF_LABEL,
            language_id: arches.activeLanguage,
            value: '',
            item_id: newLabelCounter.value,
        }],
        images: [],
        children: [],
        depth: !parent.depth ? 0 : parent.depth + 1,
    };

    nextNewItem.value = newItem;
    newLabelFormValue.value = '';
    newLabelCounter.value += 1;

    parent.children!.push(itemAsNode(newItem, selectedLanguage.value));

    expandedKeys.value = {
        ...expandedKeys.value,
        [parent.key as string]: true,
    };
    selectedKeys.value = { [newItem.id]: true };
    setDisplayedRow(newItem);
};

const onReorder = async (item: ControlledListItem, up: boolean) => {
    const list: ControlledList = findNodeInTree(tree.value, item.controlled_list_id).data;
    const siblings: ControlledListItem[] = (
        item.parent_id
        ? findNodeInTree(tree.value, item.parent_id).children.map(
            (child: TreeNode) => child.data)
        : list.items
    );

    reorderItems(list, item, siblings, up);
    const field = "sortorder";

    const success = await patchList(list, toast, $gettext, field);
    if (success) {
        const oldListIndex = tree.value.findIndex(listNode => listNode.data.id === list.id);
        tree.value = [
            ...tree.value.slice(0, oldListIndex),
            listAsNode(list, selectedLanguage.value),
            ...tree.value.slice(oldListIndex + 1),
        ];
        selectedKeys.value = {
            ...selectedKeys.value,
            [item.id]: true,
        };
    }
};
</script>

<template>
    <Button
        v-if="selectedKeys && node.key! in selectedKeys"
        v-tooltip="addChildItemLabel"
        type="button"
        raised
        class="add-child-button"
        icon="fa fa-plus"
        :aria-label="addChildItemLabel"
        @click.stop="onAddItem(node)"
    />
    <span
        v-if="!nodeIsList(node)"
        class="move-buttons"
    >
        <Button
            v-if="selectedKeys && node.key! in selectedKeys"
            v-tooltip="moveUpLabel"
            type="button"
            raised
            class="reorder-button"
            icon="fa fa-caret-up"
            :aria-label="moveUpLabel"
            :disabled="isFirstItem(node.data)"
            @click="onReorder(node.data, true)"
        />
        <Button
            v-if="selectedKeys && node.key! in selectedKeys"
            v-tooltip="moveDownLabel"
            type="button"
            raised
            class="reorder-button"
            icon="fa fa-caret-down"
            :aria-label="moveDownLabel"
            :disabled="isLastItem(node.data)"
            @click="onReorder(node.data, false)"
        />
        <Button
            v-if="!node.data.name && selectedKeys && node.key! in selectedKeys"
            v-tooltip="changeParentLabel"
            type="button"
            raised
            icon="fa fa-arrows-alt"
            :aria-label="changeParentLabel"
            @click="setMovingItem(node)"
        />
    </span>
</template>

<style scoped>
.p-button {
    background-color: aliceblue;
    color: black;
    height: 2rem;
}

.add-child-button {
    width: 2rem;
    border-radius: 50%;
}

.move-buttons {
    display: flex;
    gap: 0.5rem;
    padding-right: 0.5rem;
}

.move-button {
    height: 2.5rem;
}
</style>
