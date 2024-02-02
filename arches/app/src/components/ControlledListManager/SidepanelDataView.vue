<script setup lang="ts">
import arches from "arches";
import { computed, ref } from "vue";

import DataView from "primevue/dataview";

import SearchAddDelete from "@/components/ControlledListManager/SearchAddDelete.vue";

import type { Ref } from "vue";
import type {
    ControlledList,
    ControlledListItem,
} from "@/types/controlledListManager.d";

type Item = ControlledList | ControlledListItem;
type Items = ControlledList[] | ControlledListItem[];

const {
    addLabel,
    createItem,
    deleteItems,
    deleteLabel,
    deleteLabelPlural,
    displayedItem,
    fetchItems,
    itemLabel,
    items,
    itemsLabel,
    noItemLabel,
    noSearchResultLabel,
}: {
    addLabel: string;
    createItem: () => Promise<void>;
    deleteItems: (selectedItems: Items) => Promise<void>;
    deleteLabel: string;
    deleteLabelPlural: string;
    displayedItem: Ref<Item>;
    fetchItems: () => Promise<void>;
    items: Items;
    itemLabel: string;
    itemsLabel: string;
    noItemLabel: string;
    noSearchResultLabel: string;
} = defineProps([
    "addLabel",
    "createItem",
    "deleteItems",
    "deleteLabel",
    "deleteLabelPlural",
    "displayedItem",
    "fetchItems",
    "items",
    "itemLabel",
    "itemsLabel",
    "languageMap",
    "noItemLabel",
    "noSearchResultLabel",
]);

const selectedItems: Ref<Items> = ref([]);
const searchValue = ref("");

const filteredItems = computed(() => {
    const loweredTerm = searchValue.value.toLowerCase();
    if (!loweredTerm) {
        return items;
    }
    return items.filter((item) => {
        if (Object.hasOwn(item, "name")) {
            return (item as ControlledList).name
                .toLowerCase()
                .includes(loweredTerm);
        } else {
            // TODO: implement, see below TODO for factoring out label getter
            throw new Error();
        }
    });
});

const lightGray = "#f4f4f4";
const slateBlue = "#2d3c4b";

await fetchItems();

const toggleCheckbox = (item: ControlledList | ControlledListItem) => {
    const i = selectedItems.value.indexOf(item);
    if (i === -1) {
        selectedItems.value.push(item);
    } else {
        selectedItems.value.splice(i, 1);
    }
};

const selectAll = () => {
    selectedItems.value = items;
};
const clearAll = () => {
    selectedItems.value = [];
};
const selectRow = (item: ControlledList | ControlledListItem) => {
    displayedItem.value = item;
};
</script>

<template>
    <SearchAddDelete
        v-model="searchValue"
        :createItem="createItem"
        :addLabel="addLabel"
        :deleteItems="
            () => {
                deleteItems(selectedItems);
                selectedItems.splice(0);
            }
        "
        :deleteLabel="deleteLabel"
        :deleteLabelPlural="deleteLabelPlural"
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
                <!-- TODO(jtw): factor this out, also get appropriate language -->
                <span>{{
                    item.name ??
                    item.labels.find((label) => label.valuetype === "prefLabel")
                        ?.value ??
                    "Unlabeled item"
                }}</span>
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
