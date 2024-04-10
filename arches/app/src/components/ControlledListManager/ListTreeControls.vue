<script setup lang="ts">
import arches from "arches";
import Cookies from "js-cookie";
import { computed, inject } from "vue";
import { useGettext } from "vue3-gettext";

import { displayedRowKey, selectedLanguageKey } from "@/components/ControlledListManager/const.ts";
import {
    bestLabel,
    findItemInTree,
    itemAsNode,
    listAsNode,
} from "@/components/ControlledListManager/utils.ts";

import Button from "primevue/button";
import ConfirmDialog from "primevue/confirmdialog";
import Dropdown from "primevue/dropdown";
import { useConfirm } from "primevue/useconfirm";
import { useToast } from "primevue/usetoast";

import type { TreeExpandedKeys, TreeSelectionKeys, TreeNode } from "primevue/tree/Tree";
import type { Ref } from "@/types/Ref";
import type {
    ControlledList,
    ControlledListItem,
    NewItem,
} from "@/types/ControlledListManager";

const ERROR = "error";  // not user-facing

const { setDisplayedRow } = inject(displayedRowKey);
const selectedLanguage = inject(selectedLanguageKey);

const controlledListItemsTree = defineModel();
const expandedKeys: Ref<typeof TreeExpandedKeys> = defineModel("expandedKeys");
const selectedKeys: Ref<typeof TreeSelectionKeys> = defineModel("selectedKeys");

const { $gettext, $ngettext } = useGettext();
const ADD_NEW_LIST = $gettext("Add New List");
const ADD_CHILD_ITEM = $gettext("Add Child Item");
const lightGray = "#f4f4f4"; // todo: import from theme somewhere
const buttonGreen = "#10b981";
const buttonPink = "#ed7979";

const confirm = useConfirm();
const toast = useToast();

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

const addChild = async (parent_id: string) => {
    const newItem: NewItem = { parent_id };
    try {
        const response = await fetch(arches.urls.controlled_list_item_add, {
            method: "POST",
            headers: {
                "X-CSRFToken": Cookies.get("csrftoken"),
            },
            body: JSON.stringify(newItem),
        });
        if (response.ok) {
            const newItem = await response.json();
            const parent = findItemInTree(controlledListItemsTree.value, parent_id);
            parent.children.unshift(itemAsNode(newItem, selectedLanguage.value));
            if (parent.data.name) {
                // Parent node is a list
                parent.data.items.unshift(newItem);
            } else {
                // Parent node is an item
                parent.data.children.unshift(newItem);
            }
            expandedKeys.value = {
                ...expandedKeys.value,
                [parent.key]: true,
            };
        } else {
            throw new Error();
        }
    } catch {
        toast.add({
            severity: ERROR,
            summary: $gettext("Item creation failed"),
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


const addLabel = computed(() => {
    const selectedKeysList = Object.keys(selectedKeys.value);
    if (selectedKeysList.length === 0) {
        return ADD_NEW_LIST;
    }
    return ADD_CHILD_ITEM;
});

const onCreate = async () => {
    if (!selectedKeys.value) {
        return;
    }
    const ids = Object.keys(selectedKeys.value);
    if (ids.length === 0) {
        await createList();
    } else {
        // Button should have been disabled if there were >1 selected
        await addChild(ids[0]);
    }
};

const deleteSelected = async () => {
    if (!selectedKeys.value) {
        return;
    }
    const deletes = Object.keys(selectedKeys.value);
    if (deletes.length !== 1) {
        throw new Error('Mass deletion not yet implemented.');
    }
    const toDelete = deletes[0];
    selectedKeys.value = {};

    const allListIds = controlledListItemsTree.value.map((node: typeof TreeNode) => node.data.id);
    if (allListIds.includes(toDelete)) {
        await deleteLists(deletes);
    } else {
        await deleteItems(deletes);
    }
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
        draggable: false,
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
            :label="addLabel"
            raised
            :disabled="Object.keys(selectedKeys).length > 1"
            style="font-size: inherit"
            :pt="{ root: { style: { background: buttonGreen } } }"
            @click="onCreate"
        />
        <ConfirmDialog :draggable="false" />
        <Button
            class="list-button"
            :label="$gettext('Delete')"
            raised
            :disabled="!Object.keys(selectedKeys).length"
            :pt="{ root: { style: { background: buttonPink } } }"
            @click="confirmDelete"
        />
    </div>
    <div class="controls">
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
                root: { class: 'secondary-button' },
                input: { style: { fontFamily: 'inherit', fontSize: 'small', textAlign: 'center', alignContent: 'center' } },
                itemLabel: { style: { fontSize: 'small' } },
            }"
        />
    </div>
</template>

<style scoped>
.controls {
    display: flex;
    background: #f3fbfd;
    gap: 0.5rem;
    font-size: small;
    padding: 0.5rem;
}
.list-button {
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
    background: v-bind(lightGray);
    height: 3rem;
    margin: 0.5rem;
    justify-content: center;
    font-weight: 600;
    text-wrap: nowrap;
}
</style>

<style>
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
