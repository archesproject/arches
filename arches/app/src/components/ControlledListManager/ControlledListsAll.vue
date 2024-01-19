<script setup>
import arches from "arches";
import DataView from "primevue/dataview";

const lightGray = "#f4f4f4";
const slateBlue = "#2d3c4b";

const response = await fetch(arches.urls.controlled_lists);
const { controlled_lists: controlledLists } = await response.json();

const { selectedList } = defineProps(["selectedList"]);
</script>

<template>
    <div class="list-count">
        <span v-if="controlledLists.length" style="margin-right: 1rem">
            {{ controlledLists.length }} lists
        </span>
    </div>

    <DataView v-if="controlledLists.length" :value="controlledLists">
        <template #list="slotProps">
            <div
                v-for="(item, index) in slotProps.items"
                class="listRow"
                :class="{ selected: selectedList.value?.id === item.id }"
                :key="index"
                @click="
                    () => {
                        selectedList.value = item;
                    }
                "
            >
                <input type="checkbox" />
                <span>{{ item.name }}</span>
            </div>
        </template>
    </DataView>

    <div v-else class="no-lists">
        <span>Click "Create New List" to start.</span>
    </div>
</template>

<style scoped>
.no-lists {
    margin: 2rem;
    display: flex;
    justify-content: center;
}
.list-count {
    display: flex;
    background-color: v-bind(lightGray);
    height: 2rem;
    font-size: small;
    justify-content: right;
}
.p-dataview {
    overflow-y: auto;
    padding-bottom: 5rem;
    font-size: 14px;
}
.listRow {
    display: flex;
    padding: 1rem;
}
.listRow.selected {
    background-color: v-bind(slateBlue);
}
.listRow.selected span {
    color: white;
}
input[type="checkbox"] {
    margin-top: 0.25rem;
    margin-right: 1rem;
}
</style>
