<script setup lang="ts">
import InputText from "primevue/inputtext";
import GenericFormField from "@/arches_component_lab/generic/GenericFormField.vue";

import type { NonLocalizedTextValue } from "@/arches_component_lab/datatypes/non-localized-text/types";

const { nodeAlias, value } = defineProps<{
    nodeAlias: string;
    value: NonLocalizedTextValue | null | undefined;
}>();
</script>

<template>
    <GenericFormField
        v-bind="$attrs"
        :node-alias="nodeAlias"
        :initial-value="value?.node_value"
    >
        <InputText
            type="text"
            :fluid="true"
        />
    </GenericFormField>
</template>
