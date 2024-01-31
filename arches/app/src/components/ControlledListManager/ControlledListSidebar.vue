<script setup>
import arches from "arches";
import Cookies from "js-cookie";
import { ref } from "vue";

import { useToast } from "primevue/usetoast";

import SearchAddDelete from "./SearchAddDelete.vue";
import SidepanelDataView from "./SidepanelDataView.vue";
import Spinner from "../Spinner.vue";

const toast = useToast();

const { displayedList, languageMap } = defineProps([
    "displayedList",
    "languageMap",
]);
const filteredLists = ref([]);
const selectedLists = ref([]);
const queryMutator = ref(0);

const createList = async () => {
    try {
        const response = await fetch(arches.urls.controlled_list_add, {
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
            summary: "List creation failed",
            life: 3000,
        });
    }
};

const deleteLists = async () => {
    if (!selectedLists.value.length) {
        return;
    }
    const promises = selectedLists.value.map((list) =>
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
            if (selectedLists.value.includes(displayedList.value)) {
                displayedList.value = null;
            }
            selectedLists.value = [];

            queryMutator.value += 1;
        }
        if (responses.some((resp) => !resp.ok)) {
            throw new Error();
        }
    } catch {
        toast.add({
            severity: "error",
            summary: "One or more lists failed to delete.",
            life: 3000,
        });
    }
};
</script>

<template>
    <div class="header">
        <h4>Controlled Lists</h4>
    </div>

    <SearchAddDelete
        :addAction="createList"
        addLabel="Create New List"
        :deleteAction="deleteLists"
        deleteLabel="Delete List"
        deleteLabelPlural="Delete Lists"
        :filteredItems="filteredLists"
        :numberToDelete="selectedLists.length"
    />

    <Suspense>
        <SidepanelDataView
            :displayedItem="displayedList"
            :selectedItems="selectedLists"
            :filteredItems="filteredLists"
            :languageMap="languageMap"
            itemLabel="list"
            itemsLabel="lists"
            noSearchResultLabel="No matching lists."
            noItemLabel='Click "Create New List" to start.'
            :key="queryMutator"
        />
        <template #fallback>
            <Spinner />
        </template>
    </Suspense>
</template>

<style scoped>
.header {
    background: #f4f4f4;
    display: flex;
    align-items: center;
}
h4 {
    margin: 1rem;
}
</style>
