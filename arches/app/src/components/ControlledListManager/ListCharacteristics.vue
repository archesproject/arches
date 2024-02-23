<script setup lang="ts">
import { useGettext } from "vue3-gettext";

import ItemCharacteristic from "@/components/ControlledListManager/ItemCharacteristic.vue";

import type { ControlledList } from "@/types/ControlledListManager";

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
        <ItemCharacteristic
            :item="props.displayedList"
            :editable="props.editable"
            field="name"
            :label="$gettext('Name')"
        />
        <ItemCharacteristic
            :item="props.displayedList"
            :editable="false"
            field="dynamic"
            :label="$gettext('Dynamic')"
            :style="{ width: '4rem' }"
        />
        <ItemCharacteristic
            :item="props.displayedList"
            :editable="false"
            field="dynamic"
            :label="$gettext('List used by these nodes')"
        />
    </div>
</template>
