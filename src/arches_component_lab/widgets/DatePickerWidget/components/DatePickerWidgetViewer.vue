<script setup lang="ts">
import type {
    DateDatatypeCardXNodeXWidgetData,
    DateValue,
} from "@/arches_component_lab/datatypes/date/types.ts";

defineProps<{
    value: DateValue;
    cardXNodeXWidgetData: DateDatatypeCardXNodeXWidgetData;
}>();
</script>

<template>
    <div>{{ value?.display_value }}</div>
</template>
