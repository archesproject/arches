<script setup>
import arches from "arches";
import DataView from "primevue/dataview";

const lightGray = "#f4f4f4";
const slateBlue = "#2d3c4b";

const {
    displayedItem,
    filteredItems,
    itemLabel,
    itemsLabel,
    languageMap,
    noItemLabel,
    noSearchResultLabel,
    selectedItems,
} = defineProps([
    "displayedItem",
    "filteredItems",
    "itemLabel",
    "itemsLabel",
    "languageMap",
    "noItemLabel",
    "noSearchResultLabel",
    "selectedItems",
]);

const response = await fetch(arches.urls.controlled_lists);
const { controlled_lists: controlledLists } = await response
    .json()
    .then((data) => {
        languageMap.value = data.languages;
        filteredItems.splice(0, filteredItems.length);
        data.controlled_lists.forEach((list) => {
            filteredItems.push(list);
        });
        return data;
    });

const toggleCheckbox = (list) => {
    const i = selectedItems.indexOf(list);
    if (i === -1) {
        selectedItems.push(list);
    } else {
        selectedItems.splice(i);
    }
};

const selectAll = () => {
    selectedItems.splice(0, selectedItems.length);
    controlledLists.forEach((list) => {
        selectedItems.push(list);
    });
};
const clearAll = () => {
    selectedItems.splice(0, selectedItems.length);
};
</script>

<template>
    <div class="selection-header">
        <span v-if="controlledLists.length" style="margin-left: 1rem">
            <button v-if="selectedItems.length" @click="clearAll">
                {{ arches.translations.clearAll }}
            </button>
            <button v-else @click="selectAll">
                {{ arches.translations.selectAll }}
            </button>
        </span>
        <span v-if="controlledLists.length" style="margin-right: 1rem">
            {{ controlledLists.length }}
            {{ controlledLists.length === 1 ? itemLabel : itemsLabel }}
        </span>
    </div>

    <DataView v-if="controlledLists.length" :value="filteredItems">
        <template #list="slotProps">
            <div
                v-for="(item, index) in slotProps.items"
                class="itemRow"
                :class="{ selected: displayedItem.value?.id === item.id }"
                :key="index"
                @click="
                    () => {
                        displayedItem.value = item;
                    }
                "
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
