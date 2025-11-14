<script setup lang="ts">
import type { NonLocalizedTextValue } from "@/arches_component_lab/datatypes/non-localized-text/types";

defineProps<{
    aliasedNodeData: NonLocalizedTextValue | null;
}>();
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
