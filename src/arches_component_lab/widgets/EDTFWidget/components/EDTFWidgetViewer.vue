<script setup lang="ts">
import type { EDTFValue } from "@/arches_component_lab/datatypes/edtf/types";

defineProps<{
    aliasedNodeData: EDTFValue | null;
}>();
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
