<script setup lang="ts">
import { computed, provide, ref } from "vue";

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

function setDisplayedList(val: ControlledList | null) {
    displayedList.value = val;
}

provide("displayedList", { displayedList, setDisplayedList });
</script>

<template>
    <!-- Subtract size of arches toolbars -->
    <div style="width: calc(100vw - 50px); height: calc(100vh - 50px)">
        <div style="height: 100%">
            <component
                :is="displayedWorkspace"
                v-model:editing="editing"
            />
        </div>
    </div>
    <Toast />
</template>

<!-- Not scoped: workaround for lack of font-family in <body> -->
<style>
div {
    font-family: "Open Sans";
}
</style>
