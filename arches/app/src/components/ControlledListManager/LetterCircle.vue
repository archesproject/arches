<script setup lang="ts">
import { computed } from "vue";

import type { ControlledList, ControlledListItem, Selectable } from "@/types/ControlledListManager";

const props: { labelled: Selectable } = defineProps(["labelled"]);

const color = computed(() => {
    if ((props.labelled as ControlledList).search_only !== undefined) {
        return 'midnightblue';
    }
    const item = props.labelled as ControlledListItem;
    if (item.guide) {
        return 'bisque';
    }
    return 'darkorchid';
});

const letter = computed(() => {
    // not translated...
    if ((props.labelled as ControlledList).search_only !== undefined) {
        return 'L';
    }
    const item = props.labelled as ControlledListItem;
    if (item.guide) {
        return 'G';
    }
    return 'I';
});
</script>

<template>
    <div class="circle">
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
