<script setup lang="ts">
import type { DateDatatypeCardXNodeXWidgetData } from "@/arches_component_lab/datatypes/date/types.ts";
import type { NodeData } from "@/arches_component_lab/types";

defineProps<{
    value: NodeData | null | undefined;
    cardXNodeXWidgetData: DateDatatypeCardXNodeXWidgetData;
}>();
</script>

<template>
    <div>{{ value?.display_value }}</div>
</template>
