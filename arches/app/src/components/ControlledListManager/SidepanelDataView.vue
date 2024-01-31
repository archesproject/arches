<script setup>
import arches from "arches";
import Cookies from "js-cookie";
import { computed, ref } from "vue";

import DataView from "primevue/dataview";
import { useToast } from "primevue/usetoast";

import SearchAddDelete from "./SearchAddDelete.vue";

const {
    displayedItem,
    itemLabel,
    itemsLabel,
    languageMap,
    noItemLabel,
    noSearchResultLabel,
} = defineProps([
    "displayedItem",
    "itemLabel",
    "itemsLabel",
    "languageMap",
    "noItemLabel",
    "noSearchResultLabel",
]);

const items = ref([]);
const selectedItems = ref([]);
const searchValue = ref("");

const filteredItems = computed(() => {
    const loweredTerm = searchValue.value.toLowerCase();
    return items.value.filter(
        (item) => !loweredTerm || item.name.includes(loweredTerm)
    );
});

const toast = useToast();
const lightGray = "#f4f4f4";
const slateBlue = "#2d3c4b";

const fetchLists = async () => {
    const response = await fetch(arches.urls.controlled_lists);
    await response.json().then((data) => {
        languageMap.value = data.languages;
        items.value = data.controlled_lists;
    });
};
await fetchLists();

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
            items.value.push(newItem);
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
            if (selectedItems.value.includes(displayedItem.value)) {
                displayedItem.value = null;
            }
            selectedItems.value = [];
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

const toggleCheckbox = (list) => {
    const i = selectedItems.value.indexOf(list);
    if (i === -1) {
        selectedItems.value.push(list);
    } else {
        selectedItems.value.splice(i);
    }
};

const selectAll = () => {
    selectedItems.value = items.value;
};
const clearAll = () => {
    selectedItems.value = [];
};
const selectRow = (item) => {
    displayedItem.value = item;
};
</script>

<template>
    <SearchAddDelete
        :v-model="searchValue"
        :addAction="createList"
        addLabel="Create New List"
        :deleteAction="deleteLists"
        deleteLabel="Delete List"
        deleteLabelPlural="Delete Lists"
        :items="items"
        :numberToDelete="selectedItems.length"
    />
    <div class="selection-header">
        <span v-if="items.length" style="margin-left: 1rem">
            <button v-if="selectedItems.length" @click="clearAll">
                {{ arches.translations.clearAll }}
            </button>
            <button v-else @click="selectAll">
                {{ arches.translations.selectAll }}
            </button>
        </span>
        <span v-if="items.length" style="margin-right: 1rem">
            {{ items.length }}
            {{ items.length === 1 ? itemLabel : itemsLabel }}
        </span>
    </div>

    <DataView v-if="items.length" :value="filteredItems">
        <template #list="slotProps">
            <div
                v-for="(item, index) in slotProps.items"
                class="itemRow"
                :class="{ selected: displayedItem.value?.id === item.id }"
                :key="index"
                tabindex="0"
                @click="selectRow(item)"
                @keyup.enter="selectRow(item)"
            >
                <input
                    type="checkbox"
                    @click="toggleCheckbox(item)"
                    :checked="selectedItems.indexOf(item) > -1"
                />
                <span>{{ item.name }}</span>
            </div>
        </template>
        <template #empty>
            <div>
                <span class="no-items">{{ noSearchResultLabel }}</span>
            </div>
        </template>
    </DataView>

    <div v-else class="no-items">
        <span>{{ noItemLabel }}</span>
    </div>
</template>

<style scoped>
button {
    border: none;
    color: var(--blue-500);
    background: none;
}
.selection-header {
    display: flex;
    background-color: v-bind(lightGray);
    height: 2rem;
    font-size: small;
    justify-content: space-between;
}
.p-dataview {
    overflow-y: auto;
    padding-bottom: 5rem;
    font-size: 14px;
}
.itemRow {
    display: flex;
    padding: 1rem;
}
.itemRow.selected {
    background-color: v-bind(slateBlue);
}
.itemRow.selected span {
    color: white;
}
input[type="checkbox"] {
    margin-top: 0.25rem;
    margin-right: 1rem;
}
.no-items {
    margin: 2rem;
    display: flex;
    justify-content: center;
}
</style>
