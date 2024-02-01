<script setup lang="ts">
import { computed, ref } from "vue";

import ControlledListInventory from "./ControlledListInventory.vue";
import ControlledListEditor from "./ControlledListEditor.vue";

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
</template>

<style>
.list-editor-container {
    width: calc(100vw - 50px);
    height: 100vh;
    background: white;
    font-size: 14px;
}
</style>
