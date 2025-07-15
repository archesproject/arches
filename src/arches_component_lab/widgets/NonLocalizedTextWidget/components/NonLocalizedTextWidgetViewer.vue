<script setup lang="ts">
import type { NodeData } from "@/arches_component_lab/types.ts";

const props = defineProps<{
    value: NodeData | null | undefined;
}>();
</script>

<template>
    <div>{{ props.value?.display_value }}</div>
</template>
