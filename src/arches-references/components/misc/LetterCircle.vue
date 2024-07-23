<script setup lang="ts">
import { computed } from "vue";

import { dataIsList } from "@/controlled-lists/utils.ts";

import type { ControlledListItem, Selectable } from "@/controlled-lists/types";

const props = defineProps<{ labelled: Selectable }>();

const color = computed(() => {
    if (dataIsList(props.labelled)) {
        return "midnightblue";
    }
    const item = props.labelled as ControlledListItem;
    if (item.guide) {
        return "chocolate";
    }
    return "darkorchid";
});

const letter = computed(() => {
    // not translated...
    if (dataIsList(props.labelled)) {
        return "L";
    }
    const item = props.labelled as ControlledListItem;
    if (item.guide) {
        return "G";
    }
    return "I";
});
</script>

<template>
    <div
        class="circle"
        aria-hidden="true"
    >
        <span class="letter">{{ letter }}</span>
    </div>
</template>

<style scoped>
.circle {
    width: 1.5rem;
    height: 1.5rem;
    min-width: 1.5rem;
    border-radius: 50%;
    background-color: v-bind("color");
    font-weight: 600;
    align-self: center;
    display: grid;
}

.letter {
    text-align: center;
    align-self: center;
    font-size: x-small;
    color: white;
}
</style>
