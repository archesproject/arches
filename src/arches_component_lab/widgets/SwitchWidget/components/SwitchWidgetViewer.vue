<script setup lang="ts">
import type { BooleanValue } from "@/arches_component_lab/datatypes/boolean/types";

defineProps<{
    aliasedNodeData: BooleanValue | null;
}>();
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
