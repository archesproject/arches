<script setup lang="ts">
import { computed, ref } from "vue";

import Toast from "primevue/toast";

import ControlledListInventory from "@/components/ControlledListManager/ControlledListInventory.vue";
import ControlledListEditor from "@/components/ControlledListManager/ControlledListEditor.vue";

import type { Ref } from "@/types/Ref";
import type { ControlledList } from "@/types/ControlledListManager";

const displayedList: Ref<ControlledList | null> = ref(null);
const editing = ref(false);

const displayedWorkspace = computed(() => {
    return editing.value ? ControlledListEditor : ControlledListInventory;
});
</script>

<template>
    <component
        :is="displayedWorkspace"
        v-model:displayedList="displayedList"
        v-model:editing="editing"
    />
    <Toast />
</template>

<!-- Not scoped: workaround for lack of font-family in <body> -->
<style>
div {
    font-family: "Open Sans";
}
</style>
