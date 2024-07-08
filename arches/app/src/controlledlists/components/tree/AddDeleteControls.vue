<script setup lang="ts">
import { computed, inject, ref } from "vue";
import { useGettext } from "vue3-gettext";

import { useConfirm } from "primevue/useconfirm";
import { useToast } from "primevue/usetoast";
import Button from "primevue/button";
import ConfirmDialog from "primevue/confirmdialog";
import SplitButton from "primevue/splitbutton";

import { deleteItems, deleteLists, fetchLists } from "@/controlledlists/api.ts";
import {
    DANGER,
    DEFAULT_ERROR_TOAST_LIFE,
    ERROR,
    SUCCESS,
    displayedRowKey,
    selectedLanguageKey,
} from "@/controlledlists/constants.ts";
import { dataIsItem, listAsNode } from "@/controlledlists/utils.ts";

import type { Ref } from "vue";
import type { TreeSelectionKeys } from "primevue/tree/Tree";
import type { TreeNode } from "primevue/treenode";
import type { Language } from "@/arches/types";
import type {
    ControlledList,
    ControlledListItem,
    DisplayedRowRefAndSetter,
    NewControlledList,
} from "@/controlledlists/types";

const { displayedRow, setDisplayedRow } = inject(
    displayedRowKey,
) as DisplayedRowRefAndSetter;
const selectedLanguage = inject(selectedLanguageKey) as Ref<Language>;

const tree = defineModel<TreeNode[]>({ required: true });
const selectedKeys = defineModel<TreeSelectionKeys>("selectedKeys", {
    required: true,
});
const isMultiSelecting = defineModel<boolean>("isMultiSelecting", {
    required: true,
});
const nextNewList = defineModel<NewControlledList>("nextNewList");
const newListFormValue = defineModel<string>("newListFormValue", {
    required: true,
});

// For new list entry (input textbox)
const newListCounter = ref(1);

const { $gettext, $ngettext } = useGettext();
const confirm = useConfirm();
const toast = useToast();

const multiSelectStateFromDisplayedRow = computed(() => {
    if (!displayedRow.value) {
        return {};
    }
    const newSelectedKeys = {
        [displayedRow.value.id]: { checked: true, partialChecked: false },
    };

    const recurse = (items: ControlledListItem[]) => {
        for (const child of items) {
            newSelectedKeys[child.id] = {
                checked: false,
                partialChecked: true,
            };
            recurse(child.children);
        }
    };
    if (dataIsItem(displayedRow.value)) {
        recurse((displayedRow.value as ControlledListItem).children);
    } else {
        recurse((displayedRow.value as ControlledList).items);
    }
    return newSelectedKeys;
});

const deleteDropdownOptions = [
    {
        label: $gettext("Delete Multiple"),
        command: () => {
            isMultiSelecting.value = true;
            selectedKeys.value = { ...multiSelectStateFromDisplayedRow.value };
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
    newListFormValue.value = "";
    newListCounter.value += 1;

    tree.value.push(listAsNode(newList, selectedLanguage.value));

    selectedKeys.value = { [newList.id]: true };
    setDisplayedRow(newList);
};

const toDelete = computed(() => {
    if (!selectedKeys.value) {
        return [];
    }
    if (isMultiSelecting.value) {
        return Object.entries(selectedKeys.value)
            .filter(([, v]) => v.checked)
            .map(([k]) => k);
    }
    return Object.entries(selectedKeys.value)
        .filter(([, v]) => v)
        .map(([k]) => k);
});

const deleteSelected = async () => {
    if (!selectedKeys.value) {
        return;
    }
    const allListIds = tree.value.map((node) => node.data.id);

    const listIdsToDelete = toDelete.value.filter((id) =>
        allListIds.includes(id),
    );
    const itemIdsToDelete = toDelete.value.filter(
        (id) => !listIdsToDelete.includes(id),
    );

    selectedKeys.value = {};

    // Do items first so that cascade deletion doesn't cause item deletion to fail.
    let anyDeleted = false;
    if (itemIdsToDelete.length) {
        try {
            anyDeleted = await deleteItems(itemIdsToDelete);
        } catch (error) {
            if (error instanceof Error) {
                error.message.split("|").forEach((detail: string) => {
                    toast.add({
                        severity: ERROR,
                        life: DEFAULT_ERROR_TOAST_LIFE,
                        summary: $gettext("Item deletion failed"),
                        detail,
                    });
                });
            }
        }
    }
    if (listIdsToDelete.length) {
        try {
            anyDeleted = (await deleteLists(listIdsToDelete)) || anyDeleted;
        } catch (error) {
            if (error instanceof Error) {
                error.message.split("|").forEach((detail) => {
                    toast.add({
                        severity: ERROR,
                        life: DEFAULT_ERROR_TOAST_LIFE,
                        summary: $gettext("List deletion failed"),
                        detail,
                    });
                });
            }
        }
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
    /*
    Currently, rather than inspecting the results of the batched
    delete requests, we just refetch everything. This requires being
    a little clever about resorting the ordered response from the API
    to preserve the existing sort (and avoid confusion).
    */
    const priorSortedListIds = tree.value.map((node) => node.key);

    await fetchLists()
        .then(
            ({ controlled_lists }: { controlled_lists: ControlledList[] }) => {
                tree.value = controlled_lists
                    .map((list) => listAsNode(list, selectedLanguage.value))
                    .sort(
                        (a, b) =>
                            priorSortedListIds.indexOf(a.key) -
                            priorSortedListIds.indexOf(b.key),
                    );
            },
        )
        .catch((error: Error) => {
            toast.add({
                severity: ERROR,
                life: DEFAULT_ERROR_TOAST_LIFE,
                summary: $gettext("Unable to fetch lists"),
                detail: error.message,
            });
        });
};

await fetchListsAndPopulateTree();
</script>

<template>
    <Button
        class="list-button"
        :severity="SUCCESS"
        :label="$gettext('Add New List')"
        raised
        style="font-size: inherit"
        @click="createList"
    />
    <ConfirmDialog :draggable="false" />
    <SplitButton
        class="list-button"
        :label="$gettext('Delete')"
        :menu-button-props="{ 'aria-label': $gettext('Delete multiple') }"
        raised
        style="font-size: inherit"
        :disabled="!toDelete.length"
        :severity="DANGER"
        :model="deleteDropdownOptions"
        @click="confirmDelete"
    />
</template>

<style scoped>
.list-button,
.p-splitbutton {
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
    margin: 0; /* override arches css */
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
