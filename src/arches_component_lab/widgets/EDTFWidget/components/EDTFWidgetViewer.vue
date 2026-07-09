<script setup lang="ts">
import { onMounted } from "vue";

import type { EDTFAliasedNodeData } from "@/arches_component_lab/datatypes/edtf/types.ts";

const { aliasedNodeData } = defineProps<{
    aliasedNodeData: EDTFAliasedNodeData;
}>();

const emit = defineEmits<{
    initialized: [updatedValue: EDTFAliasedNodeData];
}>();

onMounted(() => {
    emit("initialized", aliasedNodeData);
});
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
