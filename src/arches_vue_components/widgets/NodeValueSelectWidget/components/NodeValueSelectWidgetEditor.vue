<script setup lang="ts">
import InputText from "primevue/inputtext";

import type { NodeValueAliasedNodeData } from "@/arches_vue_components/datatypes/node-value/types.ts";

defineProps<{
    aliasedNodeData: NodeValueAliasedNodeData | null;
}>();
</script>

<template>
    <InputText
        disabled
        type="text"
        :fluid="true"
        :model-value="aliasedNodeData?.node_value ?? ''"
    />
</template>
