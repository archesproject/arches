<script setup lang="ts">
import type { DomainValue } from "@/arches_component_lab/datatypes/domain/types.ts";

defineProps<{
    aliasedNodeData: DomainValue;
}>();
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
