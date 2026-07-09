<script setup lang="ts">
import { onMounted } from "vue";

import type { StringAliasedNodeData } from "@/arches_component_lab/datatypes/string/types";

const { aliasedNodeData } = defineProps<{
    aliasedNodeData: StringAliasedNodeData;
}>();

const emit = defineEmits<{
    initialized: [updatedValue: StringAliasedNodeData];
}>();

onMounted(() => {
    emit("initialized", aliasedNodeData);
});
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
