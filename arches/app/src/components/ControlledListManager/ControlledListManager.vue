<script setup>
import { computed, ref } from "vue";

import ControlledListInventory from "./ControlledListInventory.vue";
import ControlledListEditor from "./ControlledListEditor.vue";

const editingListId = ref("");
const openListEditor = (listId) => {
    editingListId.value = listId;
};

const displayedWorkspace = computed(() => {
    return editingListId.value ? ControlledListEditor : ControlledListInventory;
});
</script>

<template>
    <component
        :is="displayedWorkspace"
        :editingListId="editingListId"
        :openListEditor="openListEditor"
    />
</template>
