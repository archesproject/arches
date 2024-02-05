<script setup lang="ts">
import { computed } from "vue";
import { useGettext } from "vue3-gettext";

import type { ControlledList } from "@/types/ControlledListManager.d";

const { $gettext } = useGettext();
const slateBlue = "#2d3c4b"; // todo: import from theme somewhere

const props : {
    displayedList: ControlledList;
    isItemEditor: boolean;
} = defineProps([
    "displayedList",
    "isItemEditor",
]);

const heading = computed(() => {
    const prefix = props.isItemEditor ? $gettext("List Item Editor") : $gettext("List Editor");
    return (
        prefix + (props.displayedList ? " > " + props.displayedList.name : "")
    );
});
</script>

<template>
    <div
        class="header"
        :style="{ background: slateBlue }"
    >
        <i
            class="fa fa-inverse fa-list"
            aria-hidden="true"
        />
        <h2>{{ heading }}</h2>
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
h2 {
    font-size: 1.5rem;
    margin: 1rem;
    color: white;
}
</style>
