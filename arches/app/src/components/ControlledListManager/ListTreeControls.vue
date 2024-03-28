<script setup lang="ts">
import arches from "arches";
import Cookies from "js-cookie";
import { inject } from "vue";
import { useGettext } from "vue3-gettext";

import { displayedRowKey, selectedLanguageKey } from "@/components/ControlledListManager/const.ts";
import { bestLabel } from "@/components/ControlledListManager/utils.ts";

import Button from "primevue/button";
import Dropdown from "primevue/dropdown";
import { useToast } from "primevue/usetoast";

import type { TreeExpandedKeys, TreeSelectionKeys, TreeNode } from "primevue/tree/Tree";
import type { Ref } from "@/types/Ref";
import type {
    ControlledList,
    ControlledListItem
} from "@/types/ControlledListManager";

const ERROR = "error";  // not user-facing

const { setDisplayedRow } = inject(displayedRowKey);
const selectedLanguage = inject(selectedLanguageKey);

const controlledListItemsTree = defineModel();
const expandedKeys: Ref<typeof TreeExpandedKeys> = defineModel("expandedKeys");
const selectedKeys: Ref<typeof TreeSelectionKeys> = defineModel("selectedKeys");

const { $gettext, $ngettext } = useGettext();
const ADD_NEW_LIST = $gettext("Add New List");
const lightGray = "#f4f4f4"; // todo: import from theme somewhere
const buttonGreen = "#10b981";
const buttonPink = "#ed7979";

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

function itemAsNode(item: ControlledListItem): typeof TreeNode {
    return {
        key: item.id,
        label: bestLabel(item, selectedLanguage.value.code).value,
        children: item.children.map(child => itemAsNode(child)),
        data: item,
    };
}

function listAsNode(list: ControlledList): typeof TreeNode {
    return {
        key: list.id,
        label: list.name,
        children: list.items.map(item => itemAsNode(item)),
        data: list,
    };
}

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
                    l => listAsNode(l)
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
            const newItem = await response.json();
            controlledListItemsTree.value.unshift(listAsNode(newItem));
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

const onDelete = async () => {
    if (!selectedKeys.value) {
        return;
    }
    const toDelete = Object.keys(selectedKeys.value);
    selectedKeys.value = {};
    await deleteLists(toDelete);
    await fetchLists();
};

await fetchLists();
</script>

<template>
    <div class="controls">
        <Button
            class="list-button"
            :label="ADD_NEW_LIST"
            raised
            style="font-size: inherit"
            :pt="{ root: { style: { background: buttonGreen } } }"
            @click="createList"
        />
        <!-- We might want an are you sure? modal -->
        <Button
            class="list-button"
            :label="$ngettext('Delete List', 'Delete Lists', Object.keys(selectedKeys ?? {}).length)"
            raised
            :disabled="!Object.keys(selectedKeys).length"
            :pt="{ root: { style: { background: buttonPink } } }"
            @click="onDelete"
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
    height: 4rem;
    margin: 0.5rem;
    justify-content: center;
    font-weight: 600;
    text-wrap: nowrap;
}
</style>
