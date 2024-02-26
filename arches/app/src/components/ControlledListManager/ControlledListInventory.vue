<script setup lang="ts">
import arches from "arches";
import Cookies from "js-cookie";
import { ref } from "vue";
import { useGettext } from "vue3-gettext";

import Splitter from "primevue/splitter";
import SplitterPanel from "primevue/splitterpanel";
import { useToast } from "primevue/usetoast";

import ControlledListTable from "@/components/ControlledListManager/ControlledListTable.vue";
import SidepanelDataView from "@/components/ControlledListManager/SidepanelDataView.vue";
import SpinnerIcon from "@/components/SpinnerIcon.vue";

import type { Ref } from "@/types/Ref";
import type { ControlledList } from "@/types/ControlledListManager";

const props: {
    displayedList: ControlledList | null;
    setDisplayedList: (list: ControlledList | null) => void;
    setEditing: (val: boolean) => void;
} = defineProps([
    "displayedList",
    "setDisplayedList",
    "setEditing",
]);

const lists: Ref<ControlledList[]> = ref([]);
const toast = useToast();
const { $gettext, $ngettext } = useGettext();
const lightGray = "#f4f4f4";
const ERROR = "error";

// Strings: $gettext() is a problem in templates given <SplitterPanel> rerendering
// https://github.com/archesproject/arches/pull/10569/files#r1496212837
const CONTROLLED_LISTS = $gettext("Controlled Lists");
const CREATE_NEW_LIST = $gettext("Create New List");
const NO_MATCHING_LISTS = $gettext("No matching lists.");
const NO_SELECTION_LABEL = $gettext("Click &quot;Create New List&quot; to start.");
const DELETE_LIST = $gettext("Delete Lists");
const DELETE_LISTS = $gettext("Delete Lists");
const LIST_COUNT = $ngettext('list', 'lists', lists.value.length);

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
        props.displayedList && selectedLists.includes(props.displayedList)
    );

    try {
        const responses = await Promise.all(promises);
        if (responses.some((resp) => resp.ok)) {
            if (shouldResetDisplay) {
                props.setDisplayedList(null);
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
</script>

<template>
    <Splitter
        :pt="{
            gutter: { style: { background: lightGray } },
            gutterHandler: { style: { background: lightGray } },
        }"
    >
        <SplitterPanel
            :size="30"
            :min-size="15"
        >
            <div class="header">
                <h2>{{ CONTROLLED_LISTS }}</h2>
            </div>

            <Suspense>
                <SidepanelDataView
                    :add-label="CREATE_NEW_LIST"
                    :create-action="createList"
                    :count-label="LIST_COUNT"
                    :del-action="deleteLists"
                    :del-label="DELETE_LIST"
                    :del-label-plural="DELETE_LISTS"
                    :fetch-action="fetchLists"
                    :no-search-result-label="NO_MATCHING_LISTS"
                    :no-selection-label="NO_SELECTION_LABEL"
                    :selectables="lists"
                    :selection="displayedList"
                    :set-selection="setDisplayedList"
                />
                <template #fallback>
                    <SpinnerIcon />
                </template>
            </Suspense>
        </SplitterPanel>

        <SplitterPanel
            :size="75"
            :min-size="50"
            class="mt-0"
        >
            <ControlledListTable
                :displayed-list
                :set-editing
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
h2 {
    font-size: 1.5rem;
    margin: 1rem;
}
.p-splitter {
    width: calc(100vw - 60px);
    height: 100vh;
    background: white;
    font-size: 14px;
    border: 0;
}
.p-splitter-panel {
    display: flex;
    flex-direction: column;
}
</style>
