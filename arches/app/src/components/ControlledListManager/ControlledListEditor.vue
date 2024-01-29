<script setup>
import arches from "arches";
import Button from "primevue/button";
import Splitter from "primevue/splitter";
import SplitterPanel from "primevue/splitterpanel";

import Characteristics from "./Characteristics.vue";
import Header from "./Header.vue";

const { displayedList, editing, setEditing } = defineProps([
    "displayedList",
    "editing",
    "setEditing",
]);

const lightGray = "#f4f4f4";
</script>

<template>
    <Header :displayedList="displayedList" :isItemEditor="true"></Header>
    <div class="list-editor-container">
        <Characteristics :displayedList="displayedList" />

        <div class="items" style="margin: 1rem">
            <h4 style="margin-top: 4rem; margin-left: 0">List Item Editor</h4>
            <Splitter
                :pt="{
                    gutter: { style: { background: lightGray } },
                    gutterHandler: { style: { background: lightGray } },
                }"
            >
                <SplitterPanel :size="30" :minSize="15">
                    <div>Left</div>
                </SplitterPanel>

                <SplitterPanel :size="75" :minSize="50" class="mt-0">
                    <div>Right</div>
                </SplitterPanel>
            </Splitter>
        </div>
        <Button @click="setEditing(false)">{{
            arches.translations.return
        }}</Button>
    </div>
</template>

<style scoped>
.p-splitter {
    width: calc(100vw - 50px);
    height: calc(100vh - 400px);
    background: white;
    font-size: 14px;
}
.p-splitter-panel {
    display: flex;
    flex-direction: column;
}
</style>
