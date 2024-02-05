<script setup lang="ts">
import arches from "arches";
import { computed, ref } from "vue";
import { useGettext } from "vue3-gettext";

import DataView from "primevue/dataview";

import SearchAddDelete from "@/components/ControlledListManager/SearchAddDelete.vue";

import type { Ref } from "vue";
import type {
    ControlledList,
    ControlledListItem,
} from "@/types/ControlledListManager.d";

type Item = ControlledList | ControlledListItem;
type Items = ControlledList[] | ControlledListItem[];

const lightGray = "#f4f4f4";
const slateBlue = "#2d3c4b";
const { $gettext } = useGettext();

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
    setDisplayedItem,
}: {
    addLabel: string;
    createItem: () => Promise<void>;
    deleteItems: (selectedItems: Items) => Promise<void>;
    deleteLabel: string;
    deleteLabelPlural: string;
    displayedItem: Item;
    fetchItems: () => Promise<void>;
    items: Items;
    itemLabel: string;
    itemsLabel: string;
    noItemLabel: string;
    noSearchResultLabel: string;
    setDisplayedItem: (item: Item) => void;
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
    "setDisplayedItem",
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
    setDisplayedItem(item);
};

await fetchItems();
</script>

<template>
    <SearchAddDelete
        v-model="searchValue"
        :create-item="createItem"
        :add-label="addLabel"
        :delete-items="
            () => {
                deleteItems(selectedItems);
                selectedItems.splice(0);
            }
        "
        :delete-label="deleteLabel"
        :delete-label-plural="deleteLabelPlural"
        :number-to-delete="selectedItems.length"
    />
    <div class="selection-header">
        <span
            v-if="items.length"
            style="margin-left: 1rem"
        >
            <button
                v-if="selectedItems.length"
                @click="clearAll"
            >
                {{ arches.translations.clearAll }}
            </button>
            <button
                v-else
                @click="selectAll"
            >
                {{ arches.translations.selectAll }}
            </button>
        </span>
        <span
            v-if="items.length"
            style="margin-right: 1rem"
        >
            {{ items.length }}
            {{ items.length === 1 ? itemLabel : itemsLabel }}
        </span>
    </div>

    <DataView
        v-if="items.length"
        :value="filteredItems"
    >
        <template #list="slotProps">
            <div
                v-for="(item, index) in slotProps.items"
                :key="index"
                class="itemRow"
                :class="{ selected: displayedItem?.id === item.id }"
                tabindex="0"
                @click="selectRow(item)"
                @keyup.enter="selectRow(item)"
            >
                <input
                    type="checkbox"
                    :checked="selectedItems.indexOf(item) > -1"
                    @click="toggleCheckbox(item)"
                >
                <!-- TODO(jtw): factor this out, also get appropriate language -->
                <span>{{
                    item.name ??
                        item.labels.find((label) => label.valuetype === "prefLabel")
                            ?.value ??
                        $gettext("Unlabeled item")
                }}</span>
            </div>
        </template>
        <template #empty>
            <div>
                <span class="no-items">{{ noSearchResultLabel }}</span>
            </div>
        </template>
    </DataView>

    <div
        v-else
        class="no-items"
    >
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
