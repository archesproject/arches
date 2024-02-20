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
    Selectable,
    Selectables,
} from "@/types/ControlledListManager";

const lightGray = "#f4f4f4";
const slateBlue = "#2d3c4b";
const { $gettext } = useGettext();

const props: {
    addLabel: string;
    createAction: () => Promise<void>;
    countLabel: string;
    deleteAction: (selected: Selectables) => Promise<void>;
    deleteLabel: string;
    deleteLabelPlural: string;
    fetchAction: () => Promise<void>;
    noSearchResultLabel: string;
    noSelectionLabel: string;
    selectables: Selectables;
    selection: Selectable | null;
    setSelection: (selectable: Selectable) => void;
} = defineProps([
    "addLabel",
    "createAction",
    "countLabel",
    "deleteAction",
    "deleteLabel",
    "deleteLabelPlural",
    "fetchAction",
    "noSearchResultLabel",
    "noSelectionLabel",
    "selectables",
    "selection",
    "setSelection",
]);

const selected: Ref<Selectables> = ref([]);
const searchValue = ref("");

const bestRepresentation = (item: Selectable) => {
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

const filteredSelectables = computed(() => {
    const loweredTerm = searchValue.value.toLowerCase();
    if (!loweredTerm) {
        return props.selectables;
    }
    return props.selectables.filter((selectable) => {
        return bestRepresentation(selectable)
            .toLowerCase()
            .includes(loweredTerm);
    });
});

const rowClass = (rowData: Selectable) => {
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

const toggleCheckbox = (selectable: ControlledList | ControlledListItem) => {
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
const selectRow = (selected: ControlledList | ControlledListItem) => {
    props.setSelection(selected);
};

await props.fetchAction();
</script>

<template>
    <SearchAddDelete
        v-model="searchValue"
        :create-action
        :add-label
        :delete-action="
            () => {
                deleteAction(selected);
                selected.splice(0);
            }
        "
        :delete-label
        :delete-label-plural
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
                :class="{ selected: selection?.id === selectable.id }"
                tabindex="0"
                @click="selectRow(selectable)"
                @keyup.enter="selectRow(selectable)"
            >
                <input
                    type="checkbox"
                    :class="rowClass(selectable)"
                    :checked="selected.indexOf(selectable) > -1"
                    @click="toggleCheckbox(selectable)"
                >
                <span>{{ bestRepresentation(selectable) }}</span>
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
.no-selections {
    margin: 2rem;
    display: flex;
    justify-content: center;
}
</style>
