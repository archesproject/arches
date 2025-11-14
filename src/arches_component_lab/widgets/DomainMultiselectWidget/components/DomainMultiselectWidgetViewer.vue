<script setup lang="ts">
import type { DomainValueList } from "@/arches_component_lab/datatypes/domain/types.ts";

defineProps<{
    aliasedNodeData: DomainValueList | null;
}>();
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
