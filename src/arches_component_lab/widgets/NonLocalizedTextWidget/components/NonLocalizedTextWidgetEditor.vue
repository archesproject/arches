<script setup lang="ts">
import InputText from "primevue/inputtext";
import GenericFormField from "@/arches_component_lab/generic/GenericFormField.vue";

import type { FormFieldResolverOptions } from "@primevue/forms";
import type { NonLocalizedTextValue } from "@/arches_component_lab/datatypes/non-localized-text/types";

const { nodeAlias, value } = defineProps<{
    nodeAlias: string;
    value: NonLocalizedTextValue | null | undefined;
}>();

function resolver(event: FormFieldResolverOptions) {
    console.log("resolver", event);
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
        :initial-value="value?.node_value"
        :resolver="resolver"
    >
        <InputText
            type="text"
            :fluid="true"
        />
    </GenericFormField>
</template>
