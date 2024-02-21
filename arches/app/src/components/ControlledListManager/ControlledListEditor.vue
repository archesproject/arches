<script setup lang="ts">
import arches from "arches";
import Cookies from "js-cookie";
import { ref } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import Splitter from "primevue/splitter";
import SplitterPanel from "primevue/splitterpanel";
import { useToast } from "primevue/usetoast";

import ControlledListSplash from "@/components/ControlledListManager/ControlledListSplash.vue";
import ItemEditor from "@/components/ControlledListManager/ItemEditor.vue";
import ListCharacteristics from "@/components/ControlledListManager/ListCharacteristics.vue";
import ListHeader from "@/components/ControlledListManager/ListHeader.vue";
import SidepanelDataView from "@/components/ControlledListManager/SidepanelDataView.vue";
import SpinnerIcon from "@/components/SpinnerIcon.vue";

import type { Ref } from "vue";
import type {
    ControlledList,
    ControlledListItem,
} from "@/types/ControlledListManager";

const ERROR = "error";
const lightGray = "#f4f4f4";
const buttonGreen = "#10b981";
const toast = useToast();
const { $gettext, $ngettext } = useGettext();

const props: {
    displayedList: ControlledList;
    setEditing: (val: boolean) => void;
} = defineProps(["displayedList", "setEditing"]);

const items: Ref<ControlledListItem[]> = ref([]);
const displayedItem: Ref<ControlledListItem> = ref(null);
const setDisplayedItem = (item: ControlledListItem) => {
    displayedItem.value = item;
};

const fetchItems = async () => {
    const response = await fetch(
        arches.urls.controlled_list(props.displayedList.id)
    );
    await response.json().then((data) => {
        items.value = data.items;
    });
};

const createItem = async () => {
    try {
        const response = await fetch(arches.urls.controlled_list_item_add, {
            method: "POST",
            headers: {
                "X-CSRFToken": Cookies.get("csrftoken"),
            },
            body: JSON.stringify({ list_id: props.displayedList.id }),
        });
        if (response.ok) {
            const newItem = await response.json();
            items.value.push(newItem);
        } else {
            throw new Error();
        }
    } catch {
        toast.add({
            severity: ERROR,
            summary: $gettext("Item creation failed."),
            life: 3000,
        });
    }
};

const deleteItems = async (selectedItems: ControlledListItem[]) => {
    if (!selectedItems.length) {
        return;
    }
    const promises = selectedItems.map((item) =>
        fetch(arches.urls.controlled_list_item(item.id), {
            method: "DELETE",
            headers: {
                "X-CSRFToken": Cookies.get("csrftoken"),
            },
        })
    );

    try {
        const responses = await Promise.all(promises);
        if (responses.some((resp) => !resp.ok)) {
            throw new Error();
        }
    } catch {
        toast.add({
            severity: ERROR,
            summary: $gettext("One or more items failed to delete."),
            life: 3000,
        });
    }
    await fetchItems();
};
</script>

<template>
    <ListHeader
        :displayed-list="props.displayedList"
        :is-item-editor="true"
    />

    <div class="list-editor-container">
        <ListCharacteristics
            :displayed-list="props.displayedList"
            :editable="true"
        />

        <div
            class="items"
            style="margin: 1rem"
        >
            <h3 style="margin-top: 4rem; margin-left: 0">
                {{ $gettext("List Item Editor") }}
            </h3>
            <Splitter
                :pt="{
                    gutter: { style: { background: lightGray } },
                    gutterHandler: { style: { background: lightGray } },
                }"
            >
                <SplitterPanel
                    :size="30"
                    :min-size="15"
                >
                    <Suspense>
                        <SidepanelDataView
                            :add-label="$gettext('Add New Item')"
                            :create-action="createItem"
                            :count-label="$ngettext('item', 'items', items.length)"
                            :del-action="deleteItems"
                            :del-label="$gettext('Delete Item')"
                            :del-label-plural="$gettext('Delete Items')"
                            :fetch-action="fetchItems"
                            :no-search-result-label="
                                $gettext('No matching items.')
                            "
                            :no-selection-label="
                                $gettext(
                                    'Click &quot;Add New Item&quot; to start.'
                                )
                            "
                            :selectables="items"
                            :selection="displayedItem"
                            :set-selection="setDisplayedItem"
                        />
                        <template #fallback>
                            <SpinnerIcon />
                        </template>
                    </Suspense>
                </SplitterPanel>

                <SplitterPanel
                    :size="75"
                    :min-size="50"
                    class="item-editor-container"
                >
                    <ItemEditor
                        v-if="displayedItem"
                        :item="displayedItem"
                    />
                    <ControlledListSplash
                        v-else
                        :description="
                            $gettext('Select an item from the sidebar.')
                        "
                    />
                </SplitterPanel>
            </Splitter>
        </div>
        <Button
            raised
            class="button return"
            @click="setEditing(false)"
        >
            {{ arches.translations.return }}
        </Button>
    </div>
</template>

<style scoped>
h3 {
    font-size: 1.5rem;
}
.p-splitter {
    width: calc(100vw - 60px);
    height: calc(100vh - 450px);
    background: white;
    font-size: 14px;
}
.p-splitter-panel {
    display: flex;
    flex-direction: column;
}
.list-editor-container {
    height: 100vh;
    background: white;
    font-size: 14px;
}
.item-editor-container {
    margin-top: 0;
    overflow-y: auto;
}
.button.return {
    margin-left: 1rem;
    background: v-bind(buttonGreen);
    border: 1px solid v-bind(buttonGreen);
    color: white;
    font-weight: 600;
}
</style>
