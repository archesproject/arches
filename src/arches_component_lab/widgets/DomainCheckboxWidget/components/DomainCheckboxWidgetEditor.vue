<script setup lang="ts">
import Checkbox from "primevue/checkbox";
import CheckboxGroup from "primevue/checkboxgroup";

import type {
    DomainDatatypeCardXNodeXWidgetData,
    DomainValueList,
    DomainOption,
} from "@/arches_component_lab/datatypes/domain/types.ts";

const {
    cardXNodeXWidgetData,
    aliasedNodeData,
    shouldEmitSimplifiedValue = false,
} = defineProps<{
    cardXNodeXWidgetData: DomainDatatypeCardXNodeXWidgetData;
    aliasedNodeData: DomainValueList | null;
    shouldEmitSimplifiedValue?: boolean;
}>();

const options = cardXNodeXWidgetData.node.config.options;

const emit = defineEmits<{
    (
        event: "update:value",
        updatedValue: DomainValueList | string[] | null,
    ): void;
}>();

function onUpdateModelValue(updatedValue: string[] | null) {
    if (updatedValue?.length === 0) {
        updatedValue = null;
    }
    if (shouldEmitSimplifiedValue) {
        emit("update:value", updatedValue);
    } else {
        const updatedDisplayValue =
            updatedValue
                ?.map((domain) => {
                    const currentOption = options.find(
                        (option: DomainOption) => option.id === domain,
                    );
                    return currentOption?.text;
                })
                .join(", ") || "";

        emit("update:value", {
            display_value: updatedDisplayValue,
            node_value: updatedValue,
            details: [],
        });
    }
}
</script>

<template>
    <CheckboxGroup
        :model-value="aliasedNodeData?.node_value || []"
        class="button-group"
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
