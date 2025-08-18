<script setup lang="ts">
import type { StringValue } from "@/arches_component_lab/datatypes/string/types";

defineProps<{ aliasedNodeData?: StringValue }>();
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
