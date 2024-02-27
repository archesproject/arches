<script setup lang="ts">
import { useGettext } from "vue3-gettext";

import Splitter from "primevue/splitter";
import SplitterPanel from "primevue/splitterpanel";

import ControlledListEditor from "@/components/ControlledListManager/ControlledListEditor.vue";
import ControlledListSplash from "@/components/ControlledListManager/ControlledListSplash.vue";
import SidepanelDataView from "@/components/ControlledListManager/SidepanelDataView.vue";
import SpinnerIcon from "@/components/SpinnerIcon.vue";

import type { Ref } from "@/types/Ref";
import type { ControlledList } from "@/types/ControlledListManager";

const displayedList: Ref<ControlledList | null> = defineModel("displayedList");
const editing: Ref<boolean> = defineModel("editing");

const { $gettext } = useGettext();
const lightGray = "#f4f4f4";
const SELECT_A_LIST = $gettext("Select a list from the sidebar.");
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
                <SidepanelDataView v-model="displayedList" />
                <template #fallback>
                    <SpinnerIcon />
                </template>
            </Suspense>
        </SplitterPanel>

        <SplitterPanel
            :size="70"
            :min-size="50"
            class="mt-0"
        >
            <ControlledListEditor
                v-if="displayedList"
                :key="displayedList.id"
                v-model:editing="editing"
                :displayed-list
                :delete-lists
            />
            <ControlledListSplash
                v-else
                :description="SELECT_A_LIST"
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
    background: white;
    font-size: 14px;
    border: 0;
}
.p-splitter-panel {
    display: flex;
    flex-direction: column;
}
</style>
