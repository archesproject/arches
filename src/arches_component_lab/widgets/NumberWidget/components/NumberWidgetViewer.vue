<script setup lang="ts">
import type { NumberValue } from "@/arches_component_lab/datatypes/number/types";

defineProps<{
    aliasedNodeData: NumberValue | null;
}>();
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
