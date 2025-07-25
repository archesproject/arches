<script setup lang="ts">
import { ref, watchEffect } from "vue";

import { convertISO8601DatetimeFormatToPrimevueDatetimeFormat } from "@/arches_component_lab/widgets/DatePickerWidget/utils.ts";

import DatePicker from "primevue/datepicker";
import GenericFormField from "@/arches_component_lab/generic/GenericFormField.vue";

import { formatDate } from "@/arches_component_lab/datatypes/date/utils.ts";

import type { FormFieldResolverOptions } from "@primevue/forms";
import type {
    DateDatatypeCardXNodeXWidgetData,
    DateValue,
} from "@/arches_component_lab/datatypes/date/types.ts";

const { value, nodeAlias, cardXNodeXWidgetData } = defineProps<{
    value: DateValue;
    nodeAlias: string;
    cardXNodeXWidgetData: DateDatatypeCardXNodeXWidgetData;
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

function transformValue(event: FormFieldResolverOptions) {
    if (!event.value) {
        return null;
    }

    const formattedDate = formatDate(
        event.value,
        cardXNodeXWidgetData.node.config.dateFormat,
    );

    return {
        display_value: formattedDate,
        node_value: formattedDate,
        details: [],
    };
}
</script>

<template>
    <GenericFormField
        v-bind="$attrs"
        :node-alias="nodeAlias"
        :transform-value="transformValue"
    >
        <DatePicker
            icon-display="input"
            :date-format="dateFormat"
            :fluid="true"
            :show-time="shouldShowTime"
            :show-seconds="shouldShowTime"
            :show-icon="true"
            :manual-input="true"
            :model-value="value.node_value as unknown as Date"
        />
    </GenericFormField>
</template>
