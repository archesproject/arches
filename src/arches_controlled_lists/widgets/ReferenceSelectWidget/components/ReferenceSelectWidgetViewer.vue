<script setup lang="ts">
import type { ReferenceSelectValue } from "@/arches_controlled_lists/datatypes/reference-select/types";

defineProps<{
    aliasedNodeData: ReferenceSelectValue;
}>();
</script>

<template>
    <span>{{ aliasedNodeData.display_value }}</span>
</template>
