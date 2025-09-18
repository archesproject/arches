<script setup lang="ts">
import { computed, inject, ref } from "vue";
import { useGettext } from "vue3-gettext";

import { useConfirm } from "primevue/useconfirm";
import { useToast } from "primevue/usetoast";
import Button from "primevue/button";
import SplitButton from "primevue/splitbutton";

import ImportList from "@/arches_controlled_lists/components/misc/ImportList.vue";
import ExportList from "@/arches_controlled_lists/components/misc/ExportList.vue";

import {
    deleteItems,
    deleteLists,
    fetchLists,
} from "@/arches_controlled_lists/api.ts";
import {
    CONTRAST,
    DANGER,
    DEFAULT_ERROR_TOAST_LIFE,
    ERROR,
    PRIMARY,
    SECONDARY,
    displayedRowKey,
    selectedLanguageKey,
} from "@/arches_controlled_lists/constants.ts";
import {
    dataIsItem,
    listAsNode,
    shouldUseContrast,
} from "@/arches_controlled_lists/utils.ts";

import type { Ref } from "vue";
import type { TreeSelectionKeys } from "primevue/tree";
import type { TreeNode } from "primevue/treenode";
import type {
    ControlledList,
    ControlledListItem,
    IconLabels,
    Language,
    RowSetter,
    Selectable,
} from "@/arches_controlled_lists/types";

const { displayedRow, setDisplayedRow } = inject<{
    displayedRow: Ref<Selectable>;
    setDisplayedRow: RowSetter;
}>(displayedRowKey)!;
const selectedLanguage = inject(selectedLanguageKey) as Ref<Language>;

const tree = defineModel<TreeNode[]>({ required: true });
const selectedKeys = defineModel<TreeSelectionKeys>("selectedKeys", {
    required: true,
});
const isMultiSelecting = defineModel<boolean>("isMultiSelecting", {
    required: true,
});
const nextNewList = defineModel<ControlledList>("nextNewList");
const newListFormValue = defineModel<string>("newListFormValue", {
    required: true,
});

// For new list entry (input textbox)
const newListCounter = ref(1);

const { $gettext, $ngettext } = useGettext();
const confirm = useConfirm();
const toast = useToast();

const multiSelectStateFromDisplayedRow = computed(() => {
    if (!displayedRow.value || !displayedRow.value.id) {
        return {};
    }
    const newSelectedKeys: TreeSelectionKeys = {
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

const deleteSelectOptions = [
    {
        label: $gettext("Delete Multiple"),
        command: () => {
            isMultiSelecting.value = true;
            selectedKeys.value = { ...multiSelectStateFromDisplayedRow.value };
        },
    },
];

const iconLabels: IconLabels = {
    list: $gettext("List"),
    item: $gettext("Item"),
};

const createList = () => {
    const newList: ControlledList = {
        id: newListCounter.value.toString(),
        name: newListFormValue.value,
        dynamic: false,
        searchable: false,
        items: [],
        nodes: [],
    };

    nextNewList.value = newList;
    newListCounter.value += 1;

    tree.value.push(listAsNode(newList, selectedLanguage.value, iconLabels));

    selectedKeys.value = { [newList.id]: true };
    setDisplayedRow(newList);
};

const showImportList = ref(false);
const importDialogKey = ref(0);

const addNewListOptions = [
    {
        label: $gettext("Import from SKOS"),
        command: () => {
            importDialogKey.value++;
            showImportList.value = true;
        },
    },
];

function onImport() {
    showImportList.value = false;
    importDialogKey.value++;
    fetchListsAndPopulateTree();
}

const showExportList = ref(false);
const exportDialogKey = ref(0);

function openExportDialog() {
    exportDialogKey.value++;
    showExportList.value = true;
}

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

function parseSingleDetail(error: unknown) {
    if (!(error instanceof Error)) {
        return undefined;
    }
    return error.message.split("\n").slice(0)[0];
}

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
            toast.add({
                severity: ERROR,
                life: DEFAULT_ERROR_TOAST_LIFE,
                summary: $gettext("Item deletion failed"),
                detail: parseSingleDetail(error),
            });
        }
    }
    if (listIdsToDelete.length) {
        try {
            anyDeleted = (await deleteLists(listIdsToDelete)) || anyDeleted;
        } catch (error) {
            toast.add({
                severity: ERROR,
                life: DEFAULT_ERROR_TOAST_LIFE,
                summary: $gettext("List deletion failed"),
                detail: parseSingleDetail(error),
            });
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
        acceptProps: {
            label: $gettext("Delete"),
            severity: shouldUseContrast() ? CONTRAST : DANGER,
            style: { fontSize: "small" },
        },
        rejectProps: {
            label: $gettext("Cancel"),
            severity: shouldUseContrast() ? CONTRAST : SECONDARY,
            style: { fontSize: "small" },
        },
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
                    .map((list) =>
                        listAsNode(list, selectedLanguage.value, iconLabels),
                    )
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
    <div class="controls-container">
        <div>
            <h3 class="controls-header">
                {{ $gettext("Lists Manager") }}
            </h3>
        </div>
        <div class="button-controls-container">
            <SplitButton
                class="list-button"
                :label="$gettext('Add New List')"
                :severity="shouldUseContrast() ? CONTRAST : PRIMARY"
                :model="addNewListOptions"
                :pt="{
                    pcButton: {
                        root: { style: { width: '100%', fontSize: 'inherit' } },
                    },
                }"
                @click="createList"
            />
            <ImportList
                v-if="showImportList"
                :key="importDialogKey"
                @imported="onImport"
            />
            <Button
                class="list-button"
                :label="$gettext('Export')"
                :aria-label="$gettext('Export lists')"
                :disabled="!tree.length"
                :severity="shouldUseContrast() ? CONTRAST : PRIMARY"
                @click="openExportDialog"
            />
            <ExportList
                v-if="showExportList"
                :key="exportDialogKey"
                :lists="tree"
            />
            <SplitButton
                class="list-button"
                :label="$gettext('Delete')"
                :menu-button-props="{
                    'aria-label': $gettext('Delete multiple'),
                }"
                :disabled="!toDelete.length"
                :severity="shouldUseContrast() ? CONTRAST : DANGER"
                :model="deleteSelectOptions"
                :pt="{
                    pcButton: {
                        root: { style: { width: '100%', fontSize: 'inherit' } },
                    },
                }"
                @click="confirmDelete"
            />
        </div>
    </div>
</template>

<style scoped>
.controls-container {
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--p-content-border-color);
}

.controls-header {
    padding: 0 0.75rem;
    margin: 1rem 0 0.5rem 1rem;
    font-size: 1.75rem;
    font-weight: 400;
}

.button-controls-container {
    padding: 0 1.5rem;
    display: flex;
    gap: 0.5rem;
}

.list-button {
    height: 3rem;
    margin: 0.5rem 0;
    flex: 0.5;
    justify-content: center;
    text-wrap: nowrap;
    font-size: 1.33rem;
    font-weight: 500;
    border-radius: 2px 0 0 2px;
}

:deep(.p-splitbutton-button) {
    border-radius: 2px 0 0 2px;
}

:deep(.p-splitbutton-dropdown) {
    border-radius: 0 2px 2px 0;
}

:deep(.p-tieredmenu) {
    border-radius: 2px;
}
</style>
