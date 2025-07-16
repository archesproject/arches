<script setup lang="ts">
import InputText from "primevue/inputtext";
import GenericFormField from "@/arches_component_lab/generic/GenericFormField.vue";

import type { NodeData } from "@/arches_component_lab/types.ts";

const { nodeAlias, value } = defineProps<{
    nodeAlias: string;
    value: NodeData | null | undefined;
}>();

console.log("NonLocalizedTextWidgetEditor", nodeAlias, value);
</script>

<template>
    <GenericFormField
        v-bind="$attrs"
        :node-alias="nodeAlias"
        :initial-value="value?.interchange_value"
    >
        <InputText
            type="text"
            :fluid="true"
        />
    </GenericFormField>
</template>
