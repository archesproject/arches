<script setup lang="ts">
import arches from "arches";
import Cookies from "js-cookie";
import { ref } from "vue";

import Splitter from "primevue/splitter";
import SplitterPanel from "primevue/splitterpanel";
import { useToast } from "primevue/usetoast";

import ControlledListTable from "@/components/ControlledListManager/ControlledListTable.vue";
import SidepanelDataView from "@/components/ControlledListManager/SidepanelDataView.vue";
import Spinner from "@/components/Spinner.vue";

import type { Ref } from "vue";
import type {
    ControlledList,
    LanguageMap,
} from "@/types/ControlledListManager.d";

const {
    displayedList,
    languageMap,
    setEditing,
}: {
    displayedList: Ref<ControlledList>;
    languageMap: Ref<LanguageMap>;
    setEditing: (val: boolean) => void;
} = defineProps(["displayedList", "languageMap", "setEditing"]);

const items: Ref<ControlledList[]> = ref([]);
const toast = useToast();
const lightGray = "#f4f4f4";

const fetchLists = async () => {
    const response = await fetch(arches.urls.controlled_lists);
    await response.json().then((data) => {
        languageMap.value = data.languages;
        // Preserve reactivity of filteredLists() computed prop
        items.value.splice(0, items.value.length);
        items.value.push(...data.controlled_lists);
    });
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
            items.value.unshift(newItem);
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

const deleteLists = async (selectedItems: ControlledList[]) => {
    if (!selectedItems.length) {
        return;
    }
    const promises = selectedItems.map((list) =>
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
            if (selectedItems.includes(displayedList.value)) {
                displayedList.value = null;
            }
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
    await fetchLists();
};
</script>

<template>
    <Splitter
        :pt="{
            gutter: { style: { background: lightGray } },
            gutterHandler: { style: { background: lightGray } },
        }"
    >
        <SplitterPanel :size="30" :minSize="15">
            <div class="header">
                <h4>Controlled Lists</h4>
            </div>

            <Suspense>
                <SidepanelDataView
                    addLabel="Create New List"
                    :createItem="createList"
                    :deleteItems="deleteLists"
                    deleteLabel="Delete List"
                    deleteLabelPlural="Delete Lists"
                    :displayedItem="displayedList"
                    :fetchItems="fetchLists"
                    itemLabel="list"
                    :items="items"
                    itemsLabel="lists"
                    noSearchResultLabel="No matching lists."
                    noItemLabel='Click "Create New List" to start.'
                />
                <template #fallback>
                    <Spinner />
                </template>
            </Suspense>
        </SplitterPanel>

        <SplitterPanel :size="75" :minSize="50" class="mt-0">
            <ControlledListTable
                :displayedList="displayedList"
                :languageMap="languageMap"
                :setEditing="setEditing"
            />
        </SplitterPanel>
    </Splitter>
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
.p-splitter {
    width: calc(100vw - 50px);
    height: 100vh;
    background: white;
    font-size: 14px;
}
.p-splitter-panel {
    display: flex;
    flex-direction: column;
}
</style>
