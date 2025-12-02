<script setup lang="ts">
import { computed, ref, watchEffect } from "vue";

import { convertISO8601DatetimeFormatToPrimevueDatetimeFormat } from "@/arches_component_lab/widgets/DatePickerWidget/utils.ts";

import DatePicker from "primevue/datepicker";

import { formatDate } from "@/arches_component_lab/datatypes/date/utils.ts";

import type {
    DateDatatypeCardXNodeXWidgetData,
    DateValue,
} from "@/arches_component_lab/datatypes/date/types.ts";

const {
    cardXNodeXWidgetData,
    aliasedNodeData,
    shouldEmitSimplifiedValue = false,
} = defineProps<{
    cardXNodeXWidgetData: DateDatatypeCardXNodeXWidgetData;
    aliasedNodeData: DateValue | null;
    shouldEmitSimplifiedValue?: boolean;
}>();

const emit = defineEmits<{
    (event: "update:value", updatedValue: DateValue | string | number): void;
}>();

const shouldShowTime = ref(false);
const dateFormat = ref();

watchEffect(() => {
    const convertedDateFormat =
        convertISO8601DatetimeFormatToPrimevueDatetimeFormat(
            cardXNodeXWidgetData.node.config.dateFormat,
        );

    dateFormat.value = convertedDateFormat.dateFormat;
    shouldShowTime.value = convertedDateFormat.shouldShowTime;
});

function onUpdateModelValue(updatedValue: string) {
    const date = new Date(updatedValue);

    if (shouldEmitSimplifiedValue) {
        let simplifiedDate;
        try {
            const year = date.getFullYear();
            const month = (date.getMonth() + 1).toString().padStart(2, "0"); // Add 1 to month and pad
            const day = date.getDate().toString().padStart(2, "0");
            simplifiedDate = Number(`${year}${month}${day}`);
        } catch (_error) {
            simplifiedDate = updatedValue;
        }
        emit("update:value", simplifiedDate);
    } else {
        let formValue;
        let formattedDate;

        try {
            formattedDate = formatDate(
                date,
                cardXNodeXWidgetData.node.config.dateFormat,
            );

            formValue = {
                display_value: formattedDate,
                node_value: date.toISOString(),
                details: [],
            };
        } catch (_error) {
            formValue = {
                display_value: updatedValue,
                node_value: updatedValue,
                details: [],
            };
        }
        emit("update:value", formValue);
    }
}
const modelDate = computed(() => {
    if (!aliasedNodeData?.node_value) {
        return null;
    }
    if (shouldShowTime.value) {
        return new Date(aliasedNodeData?.node_value as string);
    }
    const incommingDate = new Date(aliasedNodeData?.node_value as string);
    const day = new Date(incommingDate).getUTCDate();
    const month = new Date(incommingDate).getUTCMonth();
    const year = new Date(incommingDate).getUTCFullYear();
    const correctedDate = new Date(year, month, day);

    return correctedDate;
});
</script>

<template>
    <DatePicker
        icon-display="input"
        :date-format="dateFormat"
        :fluid="true"
        :input-id="cardXNodeXWidgetData.node.alias"
        :manual-input="false"
        :model-value="modelDate"
        :show-time="shouldShowTime"
        :show-seconds="shouldShowTime"
        :show-icon="true"
        @update:model-value="onUpdateModelValue($event as unknown as string)"
    />
</template>
