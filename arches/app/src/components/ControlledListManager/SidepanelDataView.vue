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

const props: {
    addLabel: string;
    createItem: () => Promise<void>;
    deleteItems: (selectedItems: Items) => Promise<void>;
    deleteLabel: string;
    deleteLabelPlural: string;
    displayedItem: Item;
    fetchItems: () => Promise<void>;
    items: Items;
    itemLabel: string;
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
    "languageMap",
    "noItemLabel",
    "noSearchResultLabel",
    "setDisplayedItem",
]);

const selectedItems: Ref<Items> = ref([]);
const searchValue = ref("");

const bestRepresentation = (item: Item) => {
    if (!item) {
        return $gettext("Unlabeled Item");
    }
    if (Object.hasOwn(item, "name")) {
        return (item as ControlledList).name;
    }
    const prefLabels = (item as ControlledListItem).labels.filter(
        (label) => label.valuetype === "prefLabel"
    );
    if (!prefLabels.length) {
        // Shouldn't be possible.
        return $gettext("Unlabeled Item");
    }
    const bestLabel = prefLabels.find(
        label => label.language === arches.activeLanguage
    ) ?? prefLabels[0];
    // but is it better to fall back on altLabels?
    // consider leveraging python-side rank_label() in response
    return bestLabel.value;
};

const filteredItems = computed(() => {
    const loweredTerm = searchValue.value.toLowerCase();
    if (!loweredTerm) {
        return props.items;
    }
    return props.items.filter((item) => {
        return bestRepresentation(item)
            .toLowerCase()
            .includes(loweredTerm);
    });
});

const rowClass = (rowData: Item) => {
    if (!(rowData as ControlledListItem).depth) {
        return "";
    }
    const item = rowData as ControlledListItem;
    const depth = `depth-${item.depth}`;
    if (item.children.length) {
        return depth;
    }
    return `${depth} indented-row`;
};

const toggleCheckbox = (item: ControlledList | ControlledListItem) => {
    const i = selectedItems.value.indexOf(item);
    if (i === -1) {
        selectedItems.value.push(item);
    } else {
        selectedItems.value.splice(i, 1);
    }
};
const selectAll = () => {
    selectedItems.value = props.items;
};
const clearAll = () => {
    selectedItems.value = [];
};
const selectRow = (item: ControlledList | ControlledListItem) => {
    props.setDisplayedItem(item);
};

await props.fetchItems();
</script>

<template>
    <SearchAddDelete
        v-model="searchValue"
        :create-item
        :add-label
        :delete-items="
            () => {
                deleteItems(selectedItems);
                selectedItems.splice(0);
            }
        "
        :delete-label
        :delete-label-plural
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
            {{ itemLabel }}
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
                    :class="rowClass(item)"
                    :checked="selectedItems.indexOf(item) > -1"
                    @click="toggleCheckbox(item)"
                >
                <span>{{ bestRepresentation(item) }}</span>
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
    height: 3rem;
    font-size: small;
    justify-content: space-between;
}
.selection-header span {
    align-self: center;
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
.depth-1.indented-row {
    margin-left: 2rem;
}
.depth-2.indented-row {
    margin-left: 4rem;
}
.depth-3 > indented-row {
    margin-left: 6rem;
}
.depth-4 > indented-row {
    margin-left: 8rem;
}
.no-items {
    margin: 2rem;
    display: flex;
    justify-content: center;
}
</style>
