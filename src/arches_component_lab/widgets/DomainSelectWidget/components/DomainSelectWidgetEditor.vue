<script setup lang="ts">
import { onMounted } from "vue";
import Select from "primevue/select";

import { buildDomainAliasedNodeData } from "@/arches_component_lab/datatypes/domain/utils.ts";

import type {
    DomainAliasedNodeData,
    DomainCardXNodeXWidgetData,
} from "@/arches_component_lab/datatypes/domain/types.ts";

const { aliasedNodeData, cardXNodeXWidgetData } = defineProps<{
    cardXNodeXWidgetData?: DomainCardXNodeXWidgetData;
    aliasedNodeData: DomainAliasedNodeData | null;
}>();

const options = cardXNodeXWidgetData?.node.config.options ?? [];

const emit = defineEmits<{
    (
        event: "update:aliasedNodeData",
        updatedValue: DomainAliasedNodeData,
    ): void;
    (event: "initialized", updatedValue: DomainAliasedNodeData): void;
}>();

onMounted(() => {
    emit(
        "initialized",
        aliasedNodeData ?? buildDomainAliasedNodeData(null, options),
    );
});

function onUpdateModelValue(updatedValue: string | null) {
    emit(
        "update:aliasedNodeData",
        buildDomainAliasedNodeData(updatedValue, options),
    );
}
</script>

<template>
    <Select
        option-value="id"
        option-label="text"
        :input-id="cardXNodeXWidgetData?.node.alias"
        :options="options"
        :placeholder="cardXNodeXWidgetData?.config.placeholder"
        :fluid="true"
        :show-clear="true"
        :model-value="aliasedNodeData?.node_value ?? null"
        @update:model-value="onUpdateModelValue($event)"
    />
</template>
