<script setup lang="ts">
import { computed, ref, watchEffect } from "vue";

import { convertISO8601DatetimeFormatToPrimevueDatetimeFormat } from "@/arches_component_lab/widgets/DatePickerWidget/utils.ts";

import DatePicker from "primevue/datepicker";

import { formatDate } from "@/arches_component_lab/datatypes/date/utils.ts";

import type {
    DateDatatypeCardXNodeXWidgetData,
    DateValue,
} from "@/arches_component_lab/datatypes/date/types.ts";

const { aliasedNodeData, cardXNodeXWidgetData } = defineProps<{
    cardXNodeXWidgetData: DateDatatypeCardXNodeXWidgetData;
    aliasedNodeData: DateValue | null;
}>();

const emit = defineEmits<{
    (event: "update:value", updatedValue: DateValue): void;
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

    let formValue;

    try {
        const formattedDate = formatDate(
            date,
            cardXNodeXWidgetData.node.config.dateFormat,
        );

        formValue = {
            display_value: formattedDate,
            node_value: formattedDate,
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
const modelDate = computed(() =>
    aliasedNodeData?.node_value
        ? new Date(aliasedNodeData?.node_value as string)
        : null,
);
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
