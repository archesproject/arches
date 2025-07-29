<script setup lang="ts">
import { inject, ref, watch } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import { useToast } from "primevue/usetoast";

import { patchList } from "@/arches_controlled_lists/api.ts";
import {
    CONTRAST,
    DEFAULT_ERROR_TOAST_LIFE,
    ERROR,
    PREF_LABEL,
    PRIMARY,
    displayedRowKey,
    selectedLanguageKey,
} from "@/arches_controlled_lists/constants.ts";
import {
    dataIsItem,
    findNodeInTree,
    itemAsNode,
    listAsNode,
    nodeIsItem,
    nodeIsList,
    reorderItems,
    shouldUseContrast,
} from "@/arches_controlled_lists/utils.ts";

import type { Ref } from "vue";
import type { TreeExpandedKeys, TreeSelectionKeys } from "primevue/tree";
import type { TreeNode } from "primevue/treenode";
import type {
    ControlledList,
    ControlledListItem,
    IconLabels,
    Language,
    MoveLabels,
    RowSetter,
    Selectable,
} from "@/arches_controlled_lists/types";

const toast = useToast();
const { $gettext } = useGettext();

const selectedLanguage = inject(
    selectedLanguageKey,
) as Ref<Language> as Ref<Language>;
const { displayedRow, setDisplayedRow } = inject<{
    displayedRow: Ref<Selectable>;
    setDisplayedRow: RowSetter;
}>(displayedRowKey)!;

const { iconLabels, moveLabels, node } = defineProps<{
    iconLabels: IconLabels;
    moveLabels: MoveLabels;
    node: TreeNode;
}>();

const tree = defineModel<TreeNode[]>("tree", { required: true });
const expandedKeys = defineModel<TreeExpandedKeys>("expandedKeys", {
    required: true,
});
const selectedKeys = defineModel<TreeSelectionKeys>("selectedKeys", {
    required: true,
});
const movingItem = defineModel<TreeNode>("movingItem");
const nextNewItem = defineModel<ControlledListItem>("nextNewItem");
const newLabelCounter = ref(1);
const shouldRefocusUpArrow = ref(false);
const shouldRefocusDownArrow = ref(false);

watch(displayedRow, () => {
    shouldRefocusUpArrow.value = false;
    shouldRefocusDownArrow.value = false;
});

const isFirstItem = (item: ControlledListItem) => {
    const siblings: TreeNode[] = item.parent_id
        ? findNodeInTree(tree.value, item.parent_id).found!.data.children
        : findNodeInTree(tree.value, item.list_id).found!.data.items;
    if (!siblings.length) {
        throw new Error();
    }
    return siblings[0].id === item.id;
};

const isLastItem = (item: ControlledListItem) => {
    const siblings: TreeNode[] = item.parent_id
        ? findNodeInTree(tree.value, item.parent_id).found!.data.children
        : findNodeInTree(tree.value, item.list_id).found!.data.items;
    if (!siblings.length) {
        throw new Error();
    }
    return siblings[siblings.length - 1].id === item.id;
};

const setMovingItem = (node: TreeNode) => {
    if (!displayedRow.value || !dataIsItem(displayedRow.value)) {
        throw new Error();
    }
    movingItem.value = findNodeInTree(
        [
            itemAsNode(
                displayedRow.value as ControlledListItem,
                selectedLanguage.value,
                iconLabels,
            ),
        ],
        node.key,
    ).found;
};

const addItem = (parent: TreeNode) => {
    const newItem: ControlledListItem = {
        parent_id: nodeIsItem(parent) ? parent.data.id : null,
        id: newLabelCounter.value.toString(),
        list_id: parent.data.list_id ?? parent.data.id,
        uri: "",
        sortorder: 0,
        guide: false,
        values: [
            {
                id: "0",
                valuetype_id: PREF_LABEL,
                language_id: selectedLanguage.value.code,
                value: "",
                list_item_id: newLabelCounter.value.toString(),
            },
        ],
        images: [],
        children: [],
        depth: !parent.depth ? 0 : parent.depth + 1,
    };

    nextNewItem.value = newItem;
    newLabelCounter.value += 1;

    parent.children!.push(
        itemAsNode(newItem, selectedLanguage.value, iconLabels),
    );

    expandedKeys.value = {
        ...expandedKeys.value,
        [parent.key]: true,
    };
    selectedKeys.value = { [newItem.id]: true };
    setDisplayedRow(newItem);
};

const reorder = async (item: ControlledListItem, up: boolean) => {
    const list: ControlledList = findNodeInTree(tree.value, item.list_id).found!
        .data;

    let siblings: ControlledListItem[];
    if (item.parent_id) {
        siblings = findNodeInTree(
            tree.value,
            item.parent_id,
        ).found!.children!.map((child: TreeNode) => child.data);
    } else {
        siblings = list.items;
    }

    reorderItems(list, item, siblings, up);
    const field = "sortorder";

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
    const oldListIndex = tree.value.findIndex(
        (listNode) => listNode.data.id === list.id,
    );
    tree.value = [
        ...tree.value.slice(0, oldListIndex),
        listAsNode(list, selectedLanguage.value, iconLabels),
        ...tree.value.slice(oldListIndex + 1),
    ];
    selectedKeys.value = {
        ...selectedKeys.value,
        [item.id]: true,
    };

    if (up) {
        shouldRefocusUpArrow.value = true;
        shouldRefocusDownArrow.value = false;
    } else {
        shouldRefocusUpArrow.value = false;
        shouldRefocusDownArrow.value = true;
    }
};

const vRefocusUpArrow = {
    mounted: (el: HTMLButtonElement) => {
        if (shouldRefocusUpArrow.value && el) {
            // @ts-expect-error focusVisible not yet in typeshed
            el.focus({ focusVisible: true });
        }
    },
};
const vRefocusDownArrow = {
    mounted: (el: HTMLButtonElement) => {
        if (shouldRefocusDownArrow.value && el) {
            // @ts-expect-error focusVisible not yet in typeshed
            el.focus({ focusVisible: true });
        }
    },
};
</script>

<template>
    <Button
        v-if="selectedKeys && node.key in selectedKeys"
        v-tooltip="moveLabels.addChild"
        type="button"
        class="add-child-button"
        icon="fa fa-plus"
        :severity="shouldUseContrast() ? CONTRAST : PRIMARY"
        :aria-label="moveLabels.addChild"
        @click.stop="addItem(node)"
    />
    <span
        v-if="!nodeIsList(node)"
        class="move-buttons"
    >
        <Button
            v-if="selectedKeys && node.key in selectedKeys"
            v-refocus-up-arrow
            v-tooltip="moveLabels.moveUp"
            type="button"
            class="reorder-button"
            icon="fa fa-caret-up"
            :severity="shouldUseContrast() ? CONTRAST : PRIMARY"
            :aria-label="moveLabels.moveUp"
            :disabled="isFirstItem(node.data)"
            @click="reorder(node.data, true)"
        />
        <Button
            v-if="selectedKeys && node.key in selectedKeys"
            v-refocus-down-arrow
            v-tooltip="moveLabels.moveDown"
            type="button"
            class="reorder-button"
            icon="fa fa-caret-down"
            :severity="shouldUseContrast() ? CONTRAST : PRIMARY"
            :aria-label="moveLabels.moveDown"
            :disabled="isLastItem(node.data)"
            @click="reorder(node.data, false)"
        />
        <Button
            v-if="!node.data.name && selectedKeys && node.key in selectedKeys"
            v-tooltip="moveLabels.changeParent"
            type="button"
            icon="fa fa-arrows-alt"
            :severity="shouldUseContrast() ? CONTRAST : PRIMARY"
            :aria-label="moveLabels.changeParent"
            @click="setMovingItem(node)"
        />
    </span>
</template>

<style scoped>
.p-button {
    height: 2.5rem;
    width: 2.5rem;
    padding: 0.5rem;
    border-radius: 2px;
}

.add-child-button {
    width: 2.5rem;
    height: 2.5rem;
    font-size: 1.33rem;
    border-radius: 50%;
}

.move-buttons .p-button-icon-only {
    font-size: 1.33rem;
}

.move-buttons {
    display: flex;
    gap: 0.25rem;
    padding-inline-end: 0.5rem;
}

.move-button {
    height: 2.5rem;
}
</style>
