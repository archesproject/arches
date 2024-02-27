<script setup lang="ts">
import arches from "arches";
import Cookies from "js-cookie";
import { computed, ref } from "vue";
import { useGettext } from "vue3-gettext";

import DataView from "primevue/dataview";
import { useToast } from "primevue/usetoast";

import SearchAddDelete from "@/components/ControlledListManager/SearchAddDelete.vue";

import type { Ref } from "@/types/Ref";
import type { ControlledList } from "@/types/ControlledListManager";

const lightGray = "#f4f4f4";
const slateBlue = "#2d3c4b";
const ERROR = "error";
const { $gettext, $ngettext } = useGettext();
const toast = useToast();

const lists: Ref<ControlledList[]> = ref([]);
const displayedList: Ref<ControlledList | null> = defineModel();
const selected: Ref<ControlledList[]> = ref([]);
const searchValue = ref("");

// Strings: $gettext() is a problem in templates given <SplitterPanel> rerendering
// https://github.com/archesproject/arches/pull/10569/files#r1496212837
const NO_MATCHING_ITEMS = $gettext("No matching items.");
const NO_SELECTION_LABEL = $gettext("Click &quot;Add New Item&quot; to start.");

const filteredLists = computed(() => {
    const loweredTerm = searchValue.value.toLowerCase();
    if (!loweredTerm) {
        return lists.value;
    }
    return lists.value.filter((list) => {
        return list.name
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
    selected.value = lists.value;
};
const clearAll = () => {
    selected.value = [];
};
const selectRow = (selected: ControlledList) => {
    displayedList.value = selected;
};


const fetchLists = async () => {
    let errorText;
    try {
        const response = await fetch(arches.urls.controlled_lists);
        if (!response.ok) {
            errorText = response.statusText;
            const body = await response.json();
            errorText = body.message;
            throw new Error();
        } else {
            await response.json().then((data) => {
                lists.value = data.controlled_lists;
            });
        }
    } catch {
        toast.add({
            severity: ERROR,
            summary: errorText || $gettext("Unable to fetch lists"),
            life: 3000,
        });
    }
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
            lists.value.unshift(newItem);
        } else {
            throw new Error();
        }
    } catch {
        toast.add({
            severity: ERROR,
            summary: $gettext("List creation failed"),
            life: 3000,
        });
    }
};

const deleteLists = async (selectedLists: ControlledList[]) => {
    if (!selectedLists.length) {
        return;
    }
    const promises = selectedLists.map((list) =>
        fetch(arches.urls.controlled_list(list.id), {
            method: "DELETE",
            headers: {
                "X-CSRFToken": Cookies.get("csrftoken"),
            },
        })
    );

    const shouldResetDisplay = (
        selectedLists.some(l => l.id === displayedList.value?.id)
    );

    try {
        const responses = await Promise.all(promises);
        if (responses.some((resp) => resp.ok)) {
            if (shouldResetDisplay) {
                displayedList.value = null;
            }
        }
        responses.forEach(async (response) => {
            if (!response.ok) {
                const body = await response.json();
                toast.add({
                    severity: ERROR,
                    summary: $gettext("List deletion failed"),
                    detail: body.message,
                    life: 8000,
                });
            }
        });
    } catch {
        toast.add({
            severity: ERROR,
            summary: $gettext("List deletion failed"),
            life: 5000,
        });
    }
    await fetchLists();
};

await fetchLists();
</script>

<template>
    <SearchAddDelete
        v-model="searchValue"
        :create-action="createList"
        :del-action="
            () => {
                deleteLists(selected);
                selected.splice(0);
            }
        "
        :number-to-delete="selected.length"
    />
    <div class="selection-header">
        <span
            v-if="lists.length"
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
            v-if="lists.length"
            style="margin-right: 1rem"
        >
            {{ lists.length }}
            {{ $ngettext("list", "lists", lists.length) }}
        </span>
    </div>

    <DataView
        v-if="lists.length"
        :value="filteredLists"
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
                <span class="no-selections">{{ NO_MATCHING_ITEMS }}</span>
            </div>
        </template>
    </DataView>

    <div
        v-else
        class="no-selections"
    >
        <span>{{ NO_SELECTION_LABEL }}</span>
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
