<script setup lang="ts">
import InputText from "primevue/inputtext";
import GenericFormField from "@/arches_component_lab/generics/GenericFormField.vue";

import type { FormFieldResolverOptions } from "@primevue/forms";
import type { NonLocalizedTextValue } from "@/arches_component_lab/datatypes/non-localized-text/types";

defineProps<{
    nodeAlias: string;
    value: NonLocalizedTextValue;
}>();

function transformValueForForm(event: FormFieldResolverOptions) {
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
        :transform-value-for-form="transformValueForForm"
    >
        <InputText
            type="text"
            :fluid="true"
            :model-value="value.node_value"
        />
    </GenericFormField>
</template>
