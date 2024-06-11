<script setup lang="ts">
import { computed, inject, ref } from "vue";
import { useGettext } from "vue3-gettext";

import { useConfirm } from "primevue/useconfirm";
import { useToast } from "primevue/usetoast";
import Button from "primevue/button";
import ConfirmDialog from "primevue/confirmdialog";
import SplitButton from "primevue/splitbutton";

import { BUTTON_GREEN } from "@/theme.ts";
import { deleteItems, deleteLists, fetchLists } from "@/components/ControlledListManager/api.ts";
import { displayedRowKey, selectedLanguageKey, DANGER } from "@/components/ControlledListManager/constants.ts";
import { listAsNode } from "@/components/ControlledListManager/utils.ts";

import type { Ref } from "vue";
import type { TreeSelectionKeys } from "primevue/tree/Tree";
import type { TreeNode } from "primevue/treenode";
import type { Language } from "@/types/arches";
import type {
    ControlledList,
    DisplayedRowRefAndSetter,
    NewControlledList,
} from "@/types/ControlledListManager";

const { setDisplayedRow } = inject(displayedRowKey) as DisplayedRowRefAndSetter;
const selectedLanguage = inject(selectedLanguageKey) as Ref<Language>;

const controlledListItemsTree = defineModel<TreeNode[]>({ required: true });
const selectedKeys = defineModel<TreeSelectionKeys>("selectedKeys", { required: true });
const isMultiSelecting = defineModel<boolean>("isMultiSelecting", { required: true });
const nextNewList = defineModel<NewControlledList>("nextNewList");
const newListFormValue = defineModel<string>("newListFormValue", { required: true });

// For new list entry (input textbox)
const newListCounter = ref(1);

const { $gettext, $ngettext } = useGettext();
const confirm = useConfirm();
const toast = useToast();

const deleteDropdownOptions = [
    {
        label: $gettext("Delete Multiple"),
        command: () => {
            isMultiSelecting.value = true;
        },
    },
];

const createList = () => {
    const newList: NewControlledList = {
        id: newListCounter.value,
        name: newListFormValue.value,
        dynamic: false,
        search_only: false,
        items: [],
        nodes: [],
    };

    nextNewList.value = newList;
    newListFormValue.value = '';
    newListCounter.value += 1;

    controlledListItemsTree.value.push(listAsNode(newList, selectedLanguage.value));

    selectedKeys.value = { [newList.id]: true };
    setDisplayedRow(newList);
};

const toDelete = computed(() => {
    if (isMultiSelecting.value) {
        return Object.entries(selectedKeys.value).filter(([, v]) => v.checked).map(([k,]) => k);
    }
    return Object.entries(selectedKeys.value).filter(([, v]) => v).map(([k,]) => k);
});

const deleteSelected = async () => {
    if (!selectedKeys.value) {
        return;
    }
    const allListIds = controlledListItemsTree.value.map(node => node.data.id);

    const listIdsToDelete = toDelete.value.filter(id => allListIds.includes(id));
    const itemIdsToDelete = toDelete.value.filter(id => !listIdsToDelete.includes(id));

    selectedKeys.value = {};

    // Do items first so that cascade deletion doesn't cause item deletion to fail.
    let anyDeleted = false;
    if (itemIdsToDelete.length) {
        anyDeleted = await deleteItems(itemIdsToDelete, toast, $gettext);
    }
    if (listIdsToDelete.length) {
        anyDeleted = await deleteLists(listIdsToDelete, toast, $gettext) || anyDeleted;
    }
    if (anyDeleted) {
        setDisplayedRow(null);
    }

    isMultiSelecting.value = false;
};

const confirmDelete = () => {
    const numItems = toDelete.value.length;
    confirm.require({
        message: $ngettext(
            "Are you sure you want to delete %{numItems} item (including all children)?",
            "Are you sure you want to delete %{numItems} items (including all children)?",
            numItems,
            { numItems: numItems.toLocaleString() },
        ),
        header: $gettext("Confirm deletion"),
        icon: "fa fa-exclamation-triangle",
        rejectLabel: $gettext("Cancel"),
        rejectClass: "p-button-secondary p-button-outlined",
        acceptLabel: $gettext("Delete"),
        accept: async () => {
            await deleteSelected().then(fetchListsAndPopulateTree);
        },
        reject: () => {},
    });
};

const fetchListsAndPopulateTree = async () => {
    await fetchLists(toast, $gettext).then(
        ({ controlled_lists } : { controlled_lists: ControlledList[] }) => {
            controlledListItemsTree.value = controlled_lists.map(
                list => listAsNode(list, selectedLanguage.value)
            );
        }
    );
};

await fetchListsAndPopulateTree();
</script>

<template>
    <Button
        class="list-button"
        :label="$gettext('Add New List')"
        raised
        style="font-size: inherit"
        :pt="{ root: { style: { background: BUTTON_GREEN } } }"
        @click="createList"
    />
    <ConfirmDialog :draggable="false" />
    <SplitButton
        class="list-button"
        :label="$gettext('Delete')"
        :menu-button-props="{'aria-label': $gettext('Delete multiple')}"
        raised
        style="font-size: inherit"
        :disabled="!toDelete.length"
        :severity="DANGER"
        :model="deleteDropdownOptions"
        @click="confirmDelete"
    />
</template>

<style scoped>
.list-button, .p-splitbutton {
    height: 4rem;
    margin: 0.5rem;
    flex: 0.5;
    justify-content: center;
    font-weight: 600;
    color: white;
    text-wrap: nowrap;
}
</style>

<style>
.p-tieredmenu.p-tieredmenu-overlay {
    font-size: inherit;
}

.p-tieredmenu-root-list {
    margin: 0;  /* override arches css */
}

.p-confirm-dialog {
    font-size: small;
}

.p-dialog-header {
    background: #2d3c4b;
    color: white;
}

.p-dialog-title {
    font-weight: 800;
}

.p-dialog-content {
    padding-top: 1.25rem;
}

.p-confirm-dialog-accept {
    background: #ed7979;
    color: white;
    font-weight: 600;
}
</style>
