<script setup lang="ts">
import InputText from "primevue/inputtext";
import GenericFormField from "@/arches_component_lab/generic/GenericFormField.vue";

import type { FormFieldResolverOptions } from "@primevue/forms";
import type { NonLocalizedTextValue } from "@/arches_component_lab/datatypes/non-localized-text/types";

const { nodeAlias, value } = defineProps<{
    nodeAlias: string;
    value: NonLocalizedTextValue;
}>();

function transformValue(event: FormFieldResolverOptions) {
    return {
        display_value: event.value,
        node_value: event.value,
        details: [],
    };
}
</script>

<template>
    <GenericFormField
        v-bind="$attrs"
        :node-alias="nodeAlias"
        :transform-value="transformValue"
    >
        <InputText
            type="text"
            :fluid="true"
            :model-value="value.node_value"
        />
    </GenericFormField>
</template>
