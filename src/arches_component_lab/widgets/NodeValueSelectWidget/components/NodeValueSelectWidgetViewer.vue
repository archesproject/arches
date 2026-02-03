<script setup lang="ts">
import type { NodeValueValue } from "@/arches_component_lab/datatypes/node-value/types";

defineProps<{
    aliasedNodeData: NodeValueValue | null;
}>();
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
