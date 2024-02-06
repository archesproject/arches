<script setup lang="ts">
import { useGettext } from "vue3-gettext";

import ListCharacteristic from "@/Components/ControlledListManager/ListCharacteristic.vue";

import type { ControlledList } from "@/types/ControlledListManager.d";

const props: {
    displayedList: ControlledList;
    editable: boolean;
} = defineProps([
    "displayedList",
    "editable",
]);

const { $gettext } = useGettext();
</script>

<template>
    <div class="characteristics">
        <h3>{{ $gettext("Characteristics") }}</h3>
        <ListCharacteristic
            :displayed-list="props.displayedList"
            :editable="props.editable"
            field="name"
            :label="$gettext('Name')"
        />
        <ListCharacteristic
            :displayed-list="props.displayedList"
            :editable="false"
            field="dynamic"
            :label="$gettext('Dynamic')"
            :style="{ width: '4rem' }"
        />
        <ListCharacteristic
            :displayed-list="props.displayedList"
            :editable="false"
            :label="$gettext('List used by these nodes')"
        />
    </div>
</template>

<style scoped>
h3 {
    font-size: 1.5rem;
}.characteristics {
    padding-top: 0.125rem;
}
</style>
