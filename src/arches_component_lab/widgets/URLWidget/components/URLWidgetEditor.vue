<script setup lang="ts">
import InputText from "primevue/inputtext";

import GenericFormField from "@/arches_component_lab/generic/GenericFormField.vue";
import type { URLValue } from "@/arches_component_lab/datatypes/url/types";

const { nodeAlias, value } = defineProps<{
    nodeAlias: string;
    value: URLValue | null | undefined;
}>();
</script>

<template>
    <GenericFormField
        v-bind="$attrs"
        :node-alias="nodeAlias"
        :initial-value="value"
    >
        <InputText
            type="text"
            :fluid="true"
        />
    </GenericFormField>
</template>
