<script setup lang="ts">
import type { LanguageValue } from "@/arches_component_lab/datatypes/language/types.ts";

defineProps<{
    aliasedNodeData: LanguageValue | null;
}>();
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
