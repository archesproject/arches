<script setup lang="ts">
import type { DateDatatypeCardXNodeXWidgetData } from "@/arches_component_lab/datatypes/date/types.ts";
import type { AliasedTileNodeValue } from "@/arches_component_lab/types";

defineProps<{
    value: AliasedTileNodeValue;
    cardXNodeXWidgetData: DateDatatypeCardXNodeXWidgetData;
}>();
</script>

<template>
    <div>{{ value?.display_value }}</div>
</template>
