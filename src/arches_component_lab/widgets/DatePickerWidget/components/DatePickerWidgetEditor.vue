<script setup lang="ts">
import { ref, watchEffect } from "vue";

import { convertISO8601DatetimeFormatToPrimevueDatetimeFormat } from "@/arches_component_lab/widgets/DatePickerWidget/utils.ts";

import DatePicker from "primevue/datepicker";
import GenericFormField from "@/arches_component_lab/generics/GenericFormField.vue";

import { formatDate } from "@/arches_component_lab/datatypes/date/utils.ts";

import type { FormFieldResolverOptions } from "@primevue/forms";
import type {
    DateDatatypeCardXNodeXWidgetData,
    DateValue,
} from "@/arches_component_lab/datatypes/date/types.ts";

const props = defineProps<{
    value: DateValue;
    nodeAlias: string;
    cardXNodeXWidgetData: DateDatatypeCardXNodeXWidgetData;
}>();

type CoercedDate = Date | null;

const shouldShowTime = ref(false);
const dateFormat = ref();

watchEffect(() => {
    const convertedDateFormat =
        convertISO8601DatetimeFormatToPrimevueDatetimeFormat(
            props.cardXNodeXWidgetData.node.config.dateFormat,
        );

    dateFormat.value = convertedDateFormat.dateFormat;
    shouldShowTime.value = convertedDateFormat.shouldShowTime;
});

function transformValueForForm(event: FormFieldResolverOptions) {
    const date = new Date(event.value);

    try {
        const formattedDate = formatDate(
            date,
            props.cardXNodeXWidgetData.node.config.dateFormat,
        );

        return {
            display_value: formattedDate,
            node_value: formattedDate,
            details: [],
        };
    } catch (_error) {
        return {
            display_value: event.value,
            node_value: event.value,
            details: [],
        };
    }
}
</script>

<template>
    <GenericFormField
        v-bind="$attrs"
        :node-alias="nodeAlias"
        :transform-value-for-form="transformValueForForm"
    >
        <DatePicker
            icon-display="input"
            :date-format="dateFormat"
            :fluid="true"
            :manual-input="false"
            :model-value="value.node_value as CoercedDate"
            :show-time="shouldShowTime"
            :show-seconds="shouldShowTime"
            :show-icon="true"
        />
    </GenericFormField>
</template>
