<script setup lang="ts">
import arches from "arches";
import { computed, ref } from "vue";
import { useGettext } from "vue3-gettext";

import DataView from "primevue/dataview";

import SearchAddDelete from "@/components/ControlledListManager/SearchAddDelete.vue";

import type { Ref } from "@/types/Ref";
import type {
    ControlledList,
    Selectables,
} from "@/types/ControlledListManager";

const lightGray = "#f4f4f4";
const slateBlue = "#2d3c4b";
const { $gettext } = useGettext();

const props: {
    addLabel: string;
    createAction: () => Promise<void>;
    countLabel: string;
    delAction: (selected: Selectables) => Promise<void>;
    delLabel: string;
    delLabelPlural: string;
    fetchAction: () => Promise<void>;
    noSearchResultLabel: string;
    noSelectionLabel: string;
    selectables: ControlledList[];
} = defineProps([
    "addLabel",
    "createAction",
    "countLabel",
    "delAction",
    "delLabel",
    "delLabelPlural",
    "fetchAction",
    "noSearchResultLabel",
    "noSelectionLabel",
    "selectables",
]);

const displayedList: Ref<ControlledList | null> = defineModel();
const selected: Ref<ControlledList[]> = ref([]);
const searchValue = ref("");

const filteredSelectables = computed(() => {
    const loweredTerm = searchValue.value.toLowerCase();
    if (!loweredTerm) {
        return props.selectables;
    }
    return props.selectables.filter((selectable) => {
        return selectable.name
            .toLowerCase()
            .includes(loweredTerm);
    });
});

const toggleCheckbox = (selectable: ControlledList) => {
    const i = selected.value.indexOf(selectable);
    if (i === -1) {
        selected.value.push(selectable);
    } else {
        selected.value.splice(i, 1);
    }
};
const selectAll = () => {
    selected.value = props.selectables;
};
const clearAll = () => {
    selected.value = [];
};
const selectRow = (selected: ControlledList) => {
    displayedList.value = selected;
};

await props.fetchAction();
</script>

<template>
    <SearchAddDelete
        v-model="searchValue"
        :create-action
        :add-label
        :del-action="
            () => {
                delAction(selected);
                selected.splice(0);
            }
        "
        :del-label
        :del-label-plural
        :number-to-delete="selected.length"
    />
    <div class="selection-header">
        <span
            v-if="selectables.length"
            style="margin-left: 1rem"
        >
            <button
                v-if="selected.length"
                @click="clearAll"
            >
                {{ $gettext("Clear All") }}
            </button>
            <button
                v-else
                @click="selectAll"
            >
                {{ $gettext("Select All") }}
            </button>
        </span>
        <span
            v-if="selectables.length"
            style="margin-right: 1rem"
        >
            {{ selectables.length }}
            {{ countLabel }}
        </span>
    </div>

    <DataView
        v-if="selectables.length"
        :value="filteredSelectables"
    >
        <template #list="slotProps">
            <div
                v-for="(selectable, index) in slotProps.items"
                :key="index"
                class="itemRow"
                :class="{ selected: displayedList?.id === selectable.id }"
                tabindex="0"
                @click="selectRow(selectable)"
                @keyup.enter="selectRow(selectable)"
            >
                <input
                    type="checkbox"
                    :checked="selected.indexOf(selectable) > -1"
                    @click="toggleCheckbox(selectable)"
                >
                <span>{{ selectable.name }}</span>
            </div>
        </template>
        <template #empty>
            <div>
                <span class="no-selections">{{ noSearchResultLabel }}</span>
            </div>
        </template>
    </DataView>

    <div
        v-else
        class="no-selections"
    >
        <span>{{ noSelectionLabel }}</span>
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
.no-selections {
    margin: 2rem;
    display: flex;
    justify-content: center;
}
</style>
