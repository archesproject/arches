<script setup lang="ts">
import { useGettext } from "vue3-gettext";

import Splitter from "primevue/splitter";
import SplitterPanel from "primevue/splitterpanel";

import ControlledListSplash from "@/components/ControlledListManager/ControlledListSplash.vue";
import ListCharacteristics from "@/components/ControlledListManager/ListCharacteristics.vue";
import ListHeader from "@/components/ControlledListManager/ListHeader.vue";
import ListTree from "@/components/ControlledListManager/ListTree.vue";

import type { ControlledList } from "@/types/ControlledListManager.d";

const lightGray = "#f4f4f4";
const { $gettext } = useGettext();
const listSummary = $gettext("List Summary");
const listDetails = $gettext("List Details");

const selectAList = $gettext('Select a list from the sidebar.');

const props: {
    displayedList: ControlledList;
    setEditing: (val: boolean) => void;
} = defineProps(["displayedList", "setEditing"]);
</script>

<template>
    <ListHeader
        :displayed-list="props.displayedList"
        :is-item-editor="false"
    />

    <Splitter
        v-if="props.displayedList"
        :pt="{
            gutter: { style: { background: lightGray } },
            gutterHandler: { style: { background: lightGray } },
        }"
    >
        <SplitterPanel
            :size="40"
            :min-size="25"
        >
            <h3>{{ listSummary }}</h3>
            <ListTree
                :displayed-list
                :set-editing
            />
        </SplitterPanel>
        <SplitterPanel
            :size="60"
            :min-size="25"
        >
            <h3 style="padding-bottom: 1rem; border-bottom: 1px solid;">
                {{ listDetails }}
            </h3>
            <ListCharacteristics
                :displayed-list
                :editable="false"
            />
        </SplitterPanel>
    </Splitter>

    <ControlledListSplash
        v-else
        :description="selectAList"
    />
</template>

<style scoped>
h3 {
    font-size: 1.5rem;
    margin: 1rem;
}
.p-splitter-panel {
    margin: 1rem;
}
</style>
