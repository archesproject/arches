<script setup>
import SidepanelDataView from "./SidepanelDataView.vue";
import Spinner from "../Spinner.vue";

const { displayedList, languageMap } = defineProps([
    "displayedList",
    "languageMap",
]);
</script>

<template>
    <div class="header">
        <h4>Controlled Lists</h4>
    </div>

    <Suspense>
        <SidepanelDataView
            :displayedItem="displayedList"
            :languageMap="languageMap"
            itemLabel="list"
            itemsLabel="lists"
            noSearchResultLabel="No matching lists."
            noItemLabel='Click "Create New List" to start.'
        />
        <template #fallback>
            <Spinner />
        </template>
    </Suspense>
</template>

<style scoped>
.header {
    background: #f4f4f4;
    display: flex;
    align-items: center;
}
h4 {
    margin: 1rem;
}
</style>
