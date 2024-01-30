<script setup>
import { computed, ref } from "vue";

import ControlledListInventory from "./ControlledListInventory.vue";
import ControlledListEditor from "./ControlledListEditor.vue";

const displayedList = ref({});
const editing = ref(false);
const setEditing = (val) => {
    editing.value = val;
};

const displayedWorkspace = computed(() => {
    return editing.value ? ControlledListEditor : ControlledListInventory;
});
</script>

<template>
    <component
        :is="displayedWorkspace"
        :displayedList="displayedList"
        :setEditing="setEditing"
    />
</template>

<style>
.list-editor-container {
    width: calc(100vw - 50px);
    height: 100vh;
    background: white;
    font-size: 14px;
}
</style>
