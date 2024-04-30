<script setup lang="ts">
import arches from "arches";
import Cookies from "js-cookie";
import { inject } from "vue";
import { useGettext } from "vue3-gettext";

import { displayedRowKey, selectedLanguageKey } from "@/components/ControlledListManager/const.ts";
import { listAsNode } from "@/components/ControlledListManager/utils.ts";

import Button from "primevue/button";
import ConfirmDialog from "primevue/confirmdialog";
import Dropdown from "primevue/dropdown";
import SplitButton from "primevue/splitbutton";
import { useConfirm } from "primevue/useconfirm";
import { useToast } from "primevue/usetoast";

import type { TreeExpandedKeys, TreeSelectionKeys } from "primevue/tree/Tree";
import type { TreeNode } from "primevue/tree/Tree/TreeNode";
import type { Ref } from "@/types/Ref";
import type { ControlledList } from "@/types/ControlledListManager";

// not user-facing
const DANGER = "danger";
const ERROR = "error";

const { setDisplayedRow } = inject(displayedRowKey);
const selectedLanguage = inject(selectedLanguageKey);

const controlledListItemsTree = defineModel();
const expandedKeys: Ref<TreeExpandedKeys> = defineModel("expandedKeys");
const selectedKeys: Ref<TreeSelectionKeys> = defineModel("selectedKeys");
const movingItem: Ref<typeof TreeNode> = defineModel("movingItem");
const isMultiSelecting = defineModel("isMultiSelecting");

const { $gettext, $ngettext } = useGettext();
const buttonGreen = "#10b981";

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

const expandAll = () => {
    for (const node of controlledListItemsTree.value) {
        expandNode(node);
    }
};

const collapseAll = () => {
    expandedKeys.value = {};
};

const expandNode = (node: typeof TreeNode) => {
    if (node.children && node.children.length) {
        expandedKeys.value[node.key] = true;

        for (const child of node.children) {
            expandNode(child);
        }
    }
};

const fetchLists = async () => {
    let errorText;
    try {
        const response = await fetch(arches.urls.controlled_lists);
        if (!response.ok) {
            errorText = response.statusText;
            const body = await response.json();
            errorText = body.message;
            throw new Error();
        } else {
            await response.json().then((data) => {
                controlledListItemsTree.value = (data.controlled_lists as ControlledList[]).map(
                    l => listAsNode(l, selectedLanguage.value)
                );
            });
        }
    } catch {
        toast.add({
            severity: ERROR,
            summary: errorText || $gettext("Unable to fetch lists"),
        });
    }
};

const createList = async () => {
    try {
        const response = await fetch(arches.urls.controlled_list_add, {
            method: "POST",
            headers: {
                "X-CSRFToken": Cookies.get("csrftoken"),
            },
        });
        if (response.ok) {
            const newList = await response.json();
            controlledListItemsTree.value.unshift(listAsNode(newList));
        } else {
            throw new Error();
        }
    } catch {
        toast.add({
            severity: ERROR,
            summary: $gettext("List creation failed"),
        });
    }
};

const deleteLists = async (listIds: string[]) => {
    if (!listIds.length) {
        return;
    }
    const promises = listIds.map((id) =>
        fetch(arches.urls.controlled_list(id), {
            method: "DELETE",
            headers: {
                "X-CSRFToken": Cookies.get("csrftoken"),
            },
        })
    );

    try {
        const responses = await Promise.all(promises);
        if (responses.some((resp) => resp.ok)) {
            setDisplayedRow(null);
        }
        responses.forEach(async (response) => {
            if (!response.ok) {
                const body = await response.json();
                toast.add({
                    severity: ERROR,
                    summary: $gettext("List deletion failed"),
                    detail: body.message,
                });
            }
        });
    } catch {
        toast.add({
            severity: ERROR,
            summary: $gettext("List deletion failed"),
        });
    }
};

const deleteItems = async (itemIds: string[]) => {
    if (!itemIds.length) {
        return;
    }
    const promises = itemIds.map((id) =>
        fetch(arches.urls.controlled_list_item(id), {
            method: "DELETE",
            headers: {
                "X-CSRFToken": Cookies.get("csrftoken"),
            },
        })
    );

    try {
        const responses = await Promise.all(promises);
        if (responses.some((resp) => resp.ok)) {
            setDisplayedRow(null);
        }
        responses.forEach(async (response) => {
            if (!response.ok) {
                const body = await response.json();
                toast.add({
                    severity: ERROR,
                    summary: $gettext("Item deletion failed"),
                    detail: body.message,
                });
            }
        });
    } catch {
        toast.add({
            severity: ERROR,
            summary: $gettext("Item deletion failed"),
        });
    }
};

const deleteSelected = async () => {
    if (!selectedKeys.value) {
        return;
    }
    const deletes = Object.keys(selectedKeys.value);
    const allListIds = controlledListItemsTree.value.map((node: typeof TreeNode) => node.data.id);

    const listIdsToDelete = deletes.filter(id => allListIds.includes(id));
    const itemIdsToDelete = deletes.filter(id => !listIdsToDelete.includes(id));

    selectedKeys.value = {};

    // Do items first so that cascade deletion doesn't cause item deletion to fail.
    await deleteItems(itemIdsToDelete);
    await deleteLists(listIdsToDelete);
};

const confirmDelete = () => {
    const numItems = Object.keys(selectedKeys.value).length;
    confirm.require({
        message: $ngettext(
            "Are you sure you want to delete %{ numItems } item (including all children)?",
            "Are you sure you want to delete %{ numItems } items (including all children)?",
            numItems,
            { numItems },
        ),
        header: $gettext("Confirm deletion"),
        icon: "fa fa-exclamation-triangle",
        rejectLabel: $gettext("Cancel"),
        rejectClass: "p-button-secondary p-button-outlined",
        acceptLabel: $gettext("Delete"),
        accept: async () => {
            await deleteSelected().then(fetchLists);
        },
        reject: () => {},
    });
};

await fetchLists();
</script>

<template>
    <div class="controls">
        <Button
            class="list-button"
            :label="$gettext('Add New List')"
            raised
            style="font-size: inherit"
            :pt="{ root: { style: { background: buttonGreen } } }"
            @click="createList"
        />
        <ConfirmDialog :draggable="false" />
        <SplitButton
            class="list-button"
            :label="$gettext('Delete')"
            raised
            style="font-size: inherit"
            :disabled="!Object.keys(selectedKeys).length"
            :severity="DANGER"
            :model="deleteDropdownOptions"
            :menu-button-props="{ disabled: !Object.keys(selectedKeys).length || movingItem.key || isMultiSelecting }"
            @click="confirmDelete"
        />
    </div>

    <div
        v-if="movingItem.key"
        class="action-banner"
    >
        <!-- disable HTML escaping: RDM Admins are trusted users -->
        {{ $gettext("Selecting new parent for: %{item}", { item: movingItem.label }, true) }}
        <Button
            type="button"
            class="banner-button"
            :label="$gettext('Abandon')"
            @click="movingItem = {}"
        />
    </div>
    <div
        v-else-if="isMultiSelecting"
        class="action-banner"
    >
        {{ $gettext("Select additional items to delete") }}
        <Button
            type="button"
            class="banner-button"
            :label="$gettext('Abandon')"
            @click="isMultiSelecting = false"
        />
    </div>
    <div
        v-else
        class="controls"
    >
        <Button
            class="secondary-button"
            type="button"
            icon="fa fa-plus"
            :label="$gettext('Expand')"
            @click="expandAll"
        />
        <Button
            class="secondary-button"
            type="button"
            icon="fa fa-minus"
            :label="$gettext('Collapse')"
            @click="collapseAll"
        />
        <Dropdown
            v-model="selectedLanguage"
            :options="arches.languages"
            option-label="name"
            :placeholder="$gettext('Language')"
            checkmark
            :highlight-on-select="false"
            :pt="{
                root: { class: 'p-button secondary-button' },
                input: { style: { fontFamily: 'inherit', fontSize: 'small', textAlign: 'center', alignContent: 'center' } },
                itemLabel: { style: { fontSize: 'small' } },
            }"
        />
    </div>
</template>

<style scoped>
.action-banner {
    background: yellow;
    font-weight: 800;
    height: 5rem;
    font-size: small;
    display: flex;
    justify-content: space-between;
    padding: 1rem;
    align-items: center;
}
.banner-button {
    height: 3rem;
    background: darkslategray;
    color: white;
    text-wrap: nowrap;
}
.controls {
    display: flex;
    background: #f3fbfd;
    gap: 0.5rem;
    font-size: small;
    padding: 0.5rem;
}
.list-button, .p-splitbutton {
    height: 4rem;
    margin: 0.5rem;
    flex: 0.5;
    justify-content: center;
    font-weight: 600;
    color: white;
    text-wrap: nowrap;
}
.secondary-button {
    flex: 0.33;
    border: 0;
    background: #f4f4f4;
    height: 3rem;
    margin: 0.5rem;
    justify-content: center;
    font-weight: 600;
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
