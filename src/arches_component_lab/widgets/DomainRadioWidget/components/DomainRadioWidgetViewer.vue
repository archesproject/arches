<script setup lang="ts">
import type { DomainValue } from "@/arches_component_lab/datatypes/domain/types.ts";

defineProps<{
    aliasedNodeData: DomainValue | null;
}>();
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
