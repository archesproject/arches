<script setup>
import Splitter from "primevue/splitter";
import SplitterPanel from "primevue/splitterpanel";

import ControlledListSidebar from "./ControlledListSidebar.vue";
import ControlledListTable from "./ControlledListTable.vue";

const lightGray = "#f4f4f4";
const { displayedList, languageMap, setEditing } = defineProps([
    "displayedList",
    "languageMap",
    "setEditing",
]);
</script>

<template>
    <Splitter
        :pt="{
            gutter: { style: { background: lightGray } },
            gutterHandler: { style: { background: lightGray } },
        }"
    >
        <SplitterPanel :size="30" :minSize="15">
            <ControlledListSidebar
                :displayedList="displayedList"
                :languageMap="languageMap"
            />
        </SplitterPanel>

        <SplitterPanel :size="75" :minSize="50" class="mt-0">
            <ControlledListTable
                :displayedList="displayedList"
                :languageMap="languageMap"
                :setEditing="setEditing"
            />
        </SplitterPanel>
    </Splitter>
</template>

<style scoped>
.p-splitter {
    width: calc(100vw - 50px);
    height: 100vh;
    background: white;
    font-size: 14px;
}
.p-splitter-panel {
    display: flex;
    flex-direction: column;
}
</style>
