<script setup lang="ts">
import InputText from "primevue/inputtext";

import type { NodeValueValue } from "@/arches_component_lab/datatypes/node-value/types";

defineProps<{
    aliasedNodeData: NodeValueValue | null;
}>();
</script>

<template>
    <InputText
        disabled
        type="text"
        :fluid="true"
        :model-value="aliasedNodeData?.display_value || ''"
    />
</template>
