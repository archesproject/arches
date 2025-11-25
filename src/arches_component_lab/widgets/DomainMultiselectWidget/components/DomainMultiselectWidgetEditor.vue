<script setup lang="ts">
import MultiSelect from "primevue/multiselect";

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
    <MultiSelect
        option-value="id"
        option-label="text"
        :options="options"
        :placeholder="cardXNodeXWidgetData.config.placeholder"
        :fluid="true"
        :model-value="aliasedNodeData?.node_value || []"
        @update:model-value="onUpdateModelValue($event)"
    />
</template>
