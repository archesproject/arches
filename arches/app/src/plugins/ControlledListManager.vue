<script setup lang="ts">
import { computed, ref } from "vue";

import Toast from "primevue/toast";

import ControlledListInventory from "@/components/ControlledListManager/ControlledListInventory.vue";
import ControlledListEditor from "@/components/ControlledListManager/ControlledListEditor.vue";

import type { Ref } from "vue";
import type { ControlledList } from "@/types/ControlledListManager";

const displayedList: Ref<ControlledList | null> = ref(null);
const setDisplayedList = (list: ControlledList | null) => {
    displayedList.value = list;
};

const editing = ref(false);
const setEditing = (val: boolean) => {
    editing.value = val;
    if (!val) {
        // In future, if we desire to leave the previously
        // displayed list still displayed, ensure it has new data.
        displayedList.value = null;
    }
};

const displayedWorkspace = computed(() => {
    return editing.value ? ControlledListEditor : ControlledListInventory;
});
</script>

<template>
    <component
        :is="displayedWorkspace"
        :displayed-list="displayedList"
        :set-displayed-list="setDisplayedList"
        :set-editing="setEditing"
    />
    <Toast />
</template>

<!-- Not scoped: workaround for lack of font-family in <body> -->
<style>
div {
    font-family: "Open Sans";
}
</style>
