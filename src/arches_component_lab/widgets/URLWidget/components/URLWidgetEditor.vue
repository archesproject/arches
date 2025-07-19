<script setup lang="ts">
import InputText from "primevue/inputtext";

import GenericFormField from "@/arches_component_lab/generic/GenericFormField.vue";
import type { AliasedTileNodeValue } from "@/arches_component_lab/types.ts";

const { nodeAlias, value } = defineProps<{
    nodeAlias: string;
    value: AliasedTileNodeValue | null | undefined;
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
