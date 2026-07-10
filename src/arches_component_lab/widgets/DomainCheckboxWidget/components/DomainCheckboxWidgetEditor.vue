<script setup lang="ts">
import { onMounted } from "vue";
import Checkbox from "primevue/checkbox";
import CheckboxGroup from "primevue/checkboxgroup";

import { buildDomainListAliasedNodeData } from "@/arches_component_lab/datatypes/domain/utils.ts";

import type {
    DomainCardXNodeXWidgetData,
    DomainListAliasedNodeData,
} from "@/arches_component_lab/datatypes/domain/types.ts";

const { aliasedNodeData, cardXNodeXWidgetData } = defineProps<{
    cardXNodeXWidgetData?: DomainCardXNodeXWidgetData;
    aliasedNodeData: DomainListAliasedNodeData | null;
}>();

const options = cardXNodeXWidgetData?.node.config.options ?? [];

const emit = defineEmits<{
    (
        event: "update:aliasedNodeData",
        updatedValue: DomainListAliasedNodeData,
    ): void;
    (event: "initialized", updatedValue: DomainListAliasedNodeData): void;
}>();

onMounted(() => {
    emit(
        "initialized",
        aliasedNodeData ?? buildDomainListAliasedNodeData(null, options),
    );
});

function onUpdateModelValue(updatedValue: string[] | null) {
    const nodeValues = updatedValue?.length ? updatedValue : null;
    emit(
        "update:aliasedNodeData",
        buildDomainListAliasedNodeData(nodeValues, options),
    );
}
</script>

<template>
    <CheckboxGroup
        :id="cardXNodeXWidgetData?.node.alias"
        :model-value="aliasedNodeData?.node_value ?? []"
        class="button-group"
        tabindex="-1"
        @update:model-value="onUpdateModelValue($event)"
    >
        <div
            v-for="option of options"
            :key="option.id"
            class="button-group"
        >
            <Checkbox
                :input-id="option.id"
                :value="option.id"
            />
            <label :for="option.id">{{ option.text }}</label>
        </div>
    </CheckboxGroup>
</template>
<style scoped>
.button-group {
    display: flex;
    flex-direction: row;
    column-gap: 1.5rem;
    row-gap: 0.5rem;
    flex-wrap: wrap;
}
.checkbox-options {
    display: flex;
    gap: 0.25rem;
    align-items: center;
}
</style>
