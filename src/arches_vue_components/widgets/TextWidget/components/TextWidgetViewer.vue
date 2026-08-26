<script setup lang="ts">
import type { StringAliasedNodeData } from "@/arches_vue_components/datatypes/string/types";

defineProps<{
    aliasedNodeData: StringAliasedNodeData;
}>();
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
