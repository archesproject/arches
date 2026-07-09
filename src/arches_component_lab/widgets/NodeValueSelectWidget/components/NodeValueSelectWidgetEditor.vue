<script setup lang="ts">
import { onMounted } from "vue";
import InputText from "primevue/inputtext";

import { buildNodeValueAliasedNodeData } from "@/arches_component_lab/datatypes/node-value/utils.ts";

import type { NodeValueAliasedNodeData } from "@/arches_component_lab/datatypes/node-value/types.ts";

const { aliasedNodeData } = defineProps<{
    aliasedNodeData: NodeValueAliasedNodeData | null;
}>();

const emit = defineEmits<{
    (
        event: "update:aliasedNodeData",
        updatedValue: NodeValueAliasedNodeData,
    ): void;
    (event: "initialized", updatedValue: NodeValueAliasedNodeData): void;
}>();

onMounted(() => {
    emit("initialized", aliasedNodeData ?? buildNodeValueAliasedNodeData(null));
});
</script>

<template>
    <InputText
        disabled
        type="text"
        :fluid="true"
        :model-value="aliasedNodeData?.node_value ?? ''"
    />
</template>
