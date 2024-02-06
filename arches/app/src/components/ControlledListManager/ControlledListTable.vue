<script setup lang="ts">
import arches from "arches";
import Cookies from "js-cookie";
import { computed, ref } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import SplitButton from "primevue/splitbutton";
import { useToast } from "primevue/usetoast";

import ItemCharacteristics from "@/components/ControlledListManager/ItemCharacteristics.vue";
import ListHeader from "@/components/ControlledListManager/ListHeader.vue";

import type { Ref } from "vue";
import type {
    ControlledList,
    ControlledListItem,
    LanguageMap,
} from "@/types/ControlledListManager.d";

const buttonGreen = "#10b981";
const toast = useToast();
const { $gettext } = useGettext();

const props: {
    displayedList: ControlledList;
    languageMap: LanguageMap | null;
    setEditing: (val: boolean) => void;
} = defineProps(["displayedList", "languageMap", "setEditing"]);

const selectedLanguage: Ref<string> = ref(arches.activeLanguage);
const expandedRows = ref({});

const rowClass = (rowData: ControlledListItem) => {
    const depth = `depth-${rowData.depth}`;
    if (rowData.children.length) {
        return depth;
    }
    return `${depth} no-expander`;
};

const languageDropdownItems = computed(() => {
    if (!props.languageMap) {
        return [];
    }
    return (
        Object.entries(props.languageMap).map(([code, label]) => {
            return {
                label,
                command: () => {
                    selectedLanguage.value = code;
                },
            };
        })
    );
});

const onRowExpand = (row) => {
    expandedRows[row.data.id] = true;
};
const onRowCollapse = (row) => {
    expandedRows[row.data.id] = false;
};
const onRowReorder = (dragData) => {
    const dragDown = dragData.dropIndex > dragData.dragIndex;
    const draggedItem = props.displayedList.items[dragData.dragIndex];
    const draggedItemParent = props.displayedList.items.find(
        (item) => item.id === draggedItem.parent_id
    );
    const oldItemAtDropIndex = props.displayedList.items[dragData.dropIndex];
    const newParentId =
        dragDown && expandedRows.value[oldItemAtDropIndex.id]
            ? oldItemAtDropIndex.id
            : oldItemAtDropIndex.parent_id;

    if (newParentId !== draggedItem.parent_id) {
        // Sync expandedRows to new state of datatable (all collapsed)
        expandedRows.value = {};

        // Remove this item from old parent's children.
        if (draggedItemParent) {
            draggedItemParent.children.splice(
                draggedItemParent.children.findIndex(
                    (item) => item.id === draggedItem.id
                ),
                1
            );
            if (!draggedItemParent.children.length) {
                onRowCollapse({ data: draggedItem });
            }
        }
        // Set new parent on this item.
        draggedItem.parent_id = newParentId;
        // Add this item to new parent's children.
        if (newParentId) {
            const newParent = props.displayedList.items.find(
                (item) => item.id === newParentId
            );
            if (!newParent) {
                throw new Error();
            }
            const newParentIndex = props.displayedList.items.indexOf(newParent);
            const indexInChildren = dragData.dropIndex - newParentIndex;
            newParent.children.splice(indexInChildren, 0, draggedItem);
            draggedItem.depth = newParent.depth + 1;
        } else {
            draggedItem.depth = 0;
        }
    }

    // We don't want to make a trip to the server just to fetch
    // sort information that already agrees with the UI.
    // eslint-disable-next-line vue/no-mutating-props
    props.displayedList.items.sort((a, b) => {
        const indexInDragDataA = dragData.value.findIndex(
            (item) => item.id === a.id
        );
        const indexInDragDataB = dragData.value.findIndex(
            (item) => item.id === b.id
        );
        if (indexInDragDataA === -1 || indexInDragDataB === -1) {
            return 0;
        }
        if (indexInDragDataA < indexInDragDataB) {
            return -1;
        } else if (indexInDragDataB > indexInDragDataA) {
            return 1;
        }
        return 0;
    });
    for (let i = 0; i < props.displayedList.items.length; i++) {
        // eslint-disable-next-line vue/no-mutating-props
        props.displayedList.items[i].sortorder = i;
    }

    postDisplayedListToServer();
};

const postDisplayedListToServer = async () => {
    try {
        const response = await fetch(
            arches.urls.controlled_list(props.displayedList.id),
            {
                method: "POST",
                headers: {
                    "X-CSRFToken": Cookies.get("csrftoken"),
                },
                body: JSON.stringify(props.displayedList),
            }
        );
        if (!response.ok) {
            try {
                const body = await response.json();
                throw new Error(body.message);
            } catch {
                throw new Error(response.statusText);
            }
        }
    } catch (error) {
        toast.add({
            severity: "error",
            summary: error || $gettext("Save failed"),
            life: 3000,
        });
    }
};

const itemsForLanguage = computed(() => {
    // Show/hide rows based on row expansion toggle
    if (!props.displayedList) {
        return [];
    }
    const itemsToShow = props.displayedList.items.reduce((acc, row) => {
        if (!row.parent_id) {
            acc.push(row);
        } else if (expandedRows.value[row.parent_id]) {
            acc.push(row);
        }
        return acc;
    }, []);

    // Flatten labels
    return itemsToShow.map((item) => {
        return {
            ...item,
            prefLabels: [
                ...item.labels
                    .filter(
                        (label) =>
                            label.language === selectedLanguage.value &&
                            label.valuetype === "prefLabel"
                    )
                    .map((label) => label.value),
            ].join(", "),
            altLabels: [
                ...item.labels
                    .filter(
                        (label) =>
                            label.language === selectedLanguage.value &&
                            label.valuetype === "altLabel"
                    )
                    .map((label) => label.value),
            ].join(", "),
        };
    });
});
</script>

<template>
    <ListHeader
        :displayed-list="props.displayedList"
        :is-item-editor="false"
    />

    <div
        v-if="props.displayedList"
        class="list-editor-container"
    >
        <ItemCharacteristics
            :displayed-list="props.displayedList"
            :editable="false"
        />
        <div
            class="items"
            style="height: 50vh"
        >
            <h3 style="margin-top: 4rem; margin-left: 0">
                Items ({{ props.displayedList.items.length }})
            </h3>
            <div style="height: 100%">
                <div class="controls">
                    <SplitButton
                        class="button language-selector"
                        :label="`Language - ${languageMap?.[selectedLanguage]}`"
                        :model="languageDropdownItems"
                        raised
                        :pt="{
                            button: {
                                root: {
                                    style: {
                                        background: 'var(--gray-700)',
                                        border: '1px solid var(--gray-700)',
                                    },
                                },
                            },
                            menubutton: {
                                root: {
                                    style: {
                                        background: 'var(--gray-800)',
                                        border: '1px solid var(--gray-800)',
                                    },
                                },
                            },
                            menu: {
                                root: { class: 'language-item' },
                            },
                        }"
                    />
                    <Button
                        class="button manage-list"
                        label="Manage List"
                        raised
                        @click="() => setEditing(true)"
                    />
                </div>
                <!-- TreeTable exists, but DataTable has better support for reordering -->
                <DataTable
                    v-if="props.displayedList.items.length"
                    v-model:expandedRows="expandedRows"
                    data-key="id"
                    :value="itemsForLanguage"
                    :row-class="rowClass"
                    striped-rows
                    scrollable
                    scroll-height="flex"
                    table-style="font-size: 14px; table-layout: fixed"
                    :pt="{
                        bodyRow: { style: { height: '4rem' } },
                    }"
                    @row-expand="onRowExpand"
                    @row-collapse="onRowCollapse"
                    @row-reorder="onRowReorder"
                >
                    <Column
                        expander
                        style="width: 3rem"
                        :pt="{
                            headerCell: { style: { borderTop: 0 } },
                            headerContent: { style: { height: '5rem' } },
                        }"
                    />
                    <Column
                        row-reorder
                        style="width: 3rem"
                        :pt="{
                            headerCell: { style: { borderTop: 0 } },
                        }"
                    />
                    <Column
                        field="prefLabels"
                        :header="$gettext('Item Labels')"
                        :pt="{
                            headerCell: {
                                style: { borderTop: 0, width: '220px' },
                            },
                        }"
                    />
                    <Column
                        field="altLabels"
                        :header="$gettext('Alternate Labels')"
                        :pt="{
                            headerCell: {
                                style: { borderTop: 0, width: '220px' },
                            },
                        }"
                    />
                    <Column
                        field="uri"
                        :pt="{
                            headerCell: { style: { borderTop: 0 } },
                        }"
                    >
                        <template #header>
                            {{ $gettext("Item URI") }}
                            <i
                                v-tooltip.top="$gettext('Definition from a thesaurus or authority document')"
                                class="fa fa-info-circle"
                            />
                        </template>
                        <template #body="slotProps">
                            <a
                                :href="slotProps.data.uri"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                {{ slotProps.data.uri }}
                            </a>
                        </template>
                    </Column>
                </DataTable>
            </div>
        </div>
    </div>

    <div
        v-else
        id="rr-splash"
        class="rr-splash"
    >
        <!-- Image -->
        <div
            aria-hidden="true"
            class="img-lg img-circle rr-splash-img-container"
        >
            <i class="fa fa-list" />
        </div>

        <!-- Splash Title -->
        <div class="rr-splash-title">
            {{ $gettext("Welcome to Arches' Controlled List Manager") }}
        </div>

        <!-- Splash Instructions -->
        <div class="rr-splash-description">
            {{ $gettext("Select a list from the sidebar.") }}
        </div>
    </div>
</template>

<style scoped>
h3 {
    font-size: 1.5rem;
}
.list-editor-container {
    height: 100vh;
    background: white;
    font-size: 14px;
    margin: 1rem;
}
.controls {
    background: var(--gray-200);
}
.button {
    font-size: inherit;
    height: 4rem;
    margin: 0.5rem;
    justify-content: center;
    font-weight: 600;
    color: white;
    text-wrap: nowrap;
}
.button.manage-list {
    background: v-bind(buttonGreen);
    border: 1px solid v-bind(buttonGreen);
}
.items,
table {
    margin: inherit;
}
a {
    color: var(--blue-500);
}
i {
    margin-left: 4px;
}
</style>

<style>
.list-editor-container h3 {
    color: gray;
    border-bottom: 1px solid lightgray;
    font-weight: 400;
    margin-left: 1rem;
}
.p-tieredmenu.language-item {
    font-size: inherit;
}
.p-datatable-table {
    border: 2px solid var(--gray-200);
}
/* https://github.com/primefaces/primevue/issues/1834#issuecomment-982831184 */
.p-datatable .p-datatable-tbody > tr.no-expander > td .p-row-toggler {
    display: none;
}
.depth-1 > td:nth-child(2),
.depth-1 > td:nth-child(3) {
    padding-left: 2rem;
}
.depth-2 > td:nth-child(2),
.depth-2 > td:nth-child(3) {
    padding-left: 4rem;
}
.depth-3 > td:nth-child(2),
.depth-3 > td:nth-child(3) {
    padding-left: 6rem;
}
.depth-4 > td:nth-child(2),
.depth-4 > td:nth-child(3) {
    padding-left: 8rem;
}
</style>
