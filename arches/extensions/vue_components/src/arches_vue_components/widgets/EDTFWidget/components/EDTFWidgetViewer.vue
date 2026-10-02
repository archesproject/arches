<script setup lang="ts">
import type { EDTFAliasedNodeData } from "@/arches_vue_components/datatypes/edtf/types.ts";

defineProps<{
    aliasedNodeData: EDTFAliasedNodeData;
}>();
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
