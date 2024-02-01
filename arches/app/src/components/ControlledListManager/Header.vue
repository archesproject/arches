<script setup lang="ts">
import { computed } from "vue";

import type { Ref } from "vue";
import type { ControlledList } from "@/types/controlledListManager.d";

const slateBlue = "#2d3c4b"; // todo: import from theme somewhere

const {
    displayedList,
    isItemEditor,
}: { displayedList: Ref<ControlledList>; isItemEditor: boolean } = defineProps([
    "displayedList",
    "isItemEditor",
]);

const heading = computed(() => {
    const prefix = isItemEditor ? "List Item Editor" : "List Editor";
    return (
        prefix + (displayedList.value ? " > " + displayedList.value.name : "")
    );
});
</script>

<template>
    <div class="header" :style="{ background: slateBlue }">
        <i class="fa fa-inverse fa-list" aria-hidden="true"></i>
        <h4>{{ heading }}</h4>
    </div>
</template>

<style scoped>
.header {
    display: flex;
    align-items: center;
}
i {
    margin-left: 1rem;
    margin-top: 0.25rem;
}
h4 {
    margin: 1rem;
    color: white;
}
</style>
