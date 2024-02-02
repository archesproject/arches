<script setup lang="ts">
import { computed, ref } from "vue";

import Toast from "primevue/toast";

import ControlledListInventory from "@/components/ControlledListManager/ControlledListInventory.vue";
import ControlledListEditor from "@/components/ControlledListManager/ControlledListEditor.vue";

import type { Ref } from "vue";
import type { LanguageMap } from "@/types/controlledListManager.d";

const displayedList = ref({});
const editing = ref(false);
const languageMap: Ref<LanguageMap> = ref({});

const displayedWorkspace = computed(() => {
    return editing.value ? ControlledListEditor : ControlledListInventory;
});

const setEditing = (val: boolean) => {
    editing.value = val;
};
</script>

<template>
    <component
        :is="displayedWorkspace"
        :displayedList="displayedList"
        :languageMap="languageMap"
        :setEditing="setEditing"
    />
    <Toast />
</template>

<!-- Not scoped: workaround for lack of font-family in <body> -->
<style>
div {
    font-family: "Open Sans";
}
</style>
