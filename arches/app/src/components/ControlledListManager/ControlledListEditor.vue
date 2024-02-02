<script setup lang="ts">
import arches from "arches";
import Cookies from "js-cookie";
import { ref } from "vue";

import Button from "primevue/button";
import Splitter from "primevue/splitter";
import SplitterPanel from "primevue/splitterpanel";
import { useToast } from "primevue/usetoast";

import Characteristics from "@/components/ControlledListManager/Characteristics.vue";
import Header from "@/components/ControlledListManager/Header.vue";
import SidepanelDataView from "@/components/ControlledListManager/SidepanelDataView.vue";
import Spinner from "@/components/Spinner.vue";

import type { Ref } from "vue";
import type {
    ControlledList,
    ControlledListItem,
} from "@/types/ControlledListManager.d";

const lightGray = "#f4f4f4";
const toast = useToast();

const {
    displayedList,
    setEditing,
}: {
    displayedList: Ref<ControlledList>;
    setEditing: (val: boolean) => void;
} = defineProps(["displayedList", "setEditing"]);

const items: Ref<ControlledListItem[]> = ref([]);
const displayedItem = ref({});

const fetchItems = async () => {
    const response = await fetch(
        arches.urls.controlled_list(displayedList.value.id)
    );
    await response.json().then((data) => {
        // Preserve reactivity of filteredLists() computed prop
        items.value.splice(0, items.value.length);
        items.value.push(...data.items);
    });
};

const createItem = async () => {
    try {
        const response = await fetch(arches.urls.controlled_list_item_add, {
            method: "POST",
            headers: {
                "X-CSRFToken": Cookies.get("csrftoken"),
            },
            body: JSON.stringify({ list_id: displayedList.value.id }),
        });
        if (response.ok) {
            const newItem = await response.json();
            items.value.push(newItem);
        } else {
            throw new Error();
        }
    } catch {
        toast.add({
            severity: "error",
            summary: "Item creation failed",
            life: 3000,
        });
    }
};

const deleteItems = async (selectedItems: ControlledList[]) => {
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
            severity: "error",
            summary: "One or more items failed to delete.",
            life: 3000,
        });
    }
    await fetchItems();
};
</script>

<template>
    <Header :displayedList="displayedList" :isItemEditor="true"></Header>
    <div class="list-editor-container">
        <Characteristics :displayedList="displayedList" :editable="true" />

        <div class="items" style="margin: 1rem">
            <h3 style="margin-top: 4rem; margin-left: 0">List Item Editor</h3>
            <Splitter
                :pt="{
                    gutter: { style: { background: lightGray } },
                    gutterHandler: { style: { background: lightGray } },
                }"
            >
                <SplitterPanel :size="30" :minSize="15">
                    <Suspense>
                        <SidepanelDataView
                            addLabel="Add New Item"
                            deleteLabel="Delete Item"
                            deleteLabelPlural="Delete Items"
                            :displayedItem="displayedItem"
                            :createItem="createItem"
                            :deleteItems="deleteItems"
                            :fetchItems="fetchItems"
                            itemLabel="item"
                            :items="items"
                            itemsLabel="items"
                            noSearchResultLabel="No matching items."
                            noItemLabel='Click "Add New Item" to start.'
                        />
                        <template #fallback>
                            <Spinner />
                        </template>
                    </Suspense>
                </SplitterPanel>

                <SplitterPanel :size="75" :minSize="50" class="mt-0">
                    <div>Right</div>
                </SplitterPanel>
            </Splitter>
        </div>
        <Button @click="setEditing(false)">{{
            arches.translations.return
        }}</Button>
    </div>
</template>

<style scoped>
h3 {
    font-size: 1.5rem;
}
.p-splitter {
    width: calc(100vw - 50px);
    height: calc(100vh - 400px);
    background: white;
    font-size: 14px;
}
.p-splitter-panel {
    display: flex;
    flex-direction: column;
}
.list-editor-container {
    width: calc(100vw - 50px);
    height: 100vh;
    background: white;
    font-size: 14px;
}
</style>
