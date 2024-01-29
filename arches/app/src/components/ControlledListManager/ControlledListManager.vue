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
    <KeepAlive>
        <component
            :is="displayedWorkspace"
            :displayedList="displayedList"
            :setEditing="setEditing"
        />
    </KeepAlive>
</template>
