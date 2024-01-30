<script setup>
import arches from "arches";
import Cookies from "js-cookie";
import { ref } from "vue";

import Button from "primevue/button";
import Splitter from "primevue/splitter";
import SplitterPanel from "primevue/splitterpanel";
import { useToast } from "primevue/usetoast";

import Characteristics from "./Characteristics.vue";
import Header from "./Header.vue";
import SearchAddDelete from "./SearchAddDelete.vue";

const toast = useToast();
const lightGray = "#f4f4f4";
const { controlledLists, displayedList, queryMutator, setEditing } =
    defineProps([
        "controlledLists",
        "displayedList",
        "queryMutator",
        "setEditing",
    ]);

const selectedItems = ref([]);

const createItem = async () => {
    try {
        const response = await fetch(arches.urls.controlled_lists, {
            method: "POST",
            headers: {
                "X-CSRFToken": Cookies.get("csrftoken"),
            },
        });
        if (response.ok) {
            queryMutator.value += 1;
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

const deleteItems = async () => {
    if (!selectedItems.value.length) {
        return;
    }
    const promises = selectedItems.value.map((list) =>
        fetch(arches.urls.controlled_list(list.id), {
            method: "DELETE",
            headers: {
                "X-CSRFToken": Cookies.get("csrftoken"),
            },
        })
    );

    try {
        const responses = await Promise.all(promises);
        if (responses.some((resp) => resp.ok)) {
            if (selectedItems.value.includes(displayedList.value)) {
                displayedList.value = null;
            }
            selectedItems.value = [];

            queryMutator.value += 1;
        }
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
};
</script>

<template>
    <Header :displayedList="displayedList" :isItemEditor="true"></Header>
    <div class="list-editor-container">
        <Characteristics :displayedList="displayedList" />

        <div class="items" style="margin: 1rem">
            <h4 style="margin-top: 4rem; margin-left: 0">List Item Editor</h4>
            <Splitter
                :pt="{
                    gutter: { style: { background: lightGray } },
                    gutterHandler: { style: { background: lightGray } },
                }"
            >
                <SplitterPanel :size="30" :minSize="15">
                    <SearchAddDelete
                        :addAction="createItem"
                        addLabel="Add New Item"
                        filteredItems="[]"
                        :deleteAction="deleteItems"
                        deleteLabel="Delete Item"
                        deleteLabelPlural="Delete Items"
                        :numberToDelete="selectedItems.length"
                    />
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
</style>
