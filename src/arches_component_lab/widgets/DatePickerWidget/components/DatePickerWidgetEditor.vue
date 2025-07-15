<script setup lang="ts">
import { ref, watchEffect } from "vue";

import { convertISO8601DatetimeFormatToPrimevueDatetimeFormat } from "@/arches_component_lab/widgets/DatePickerWidget/utils.ts";

import DatePicker from "primevue/datepicker";
import GenericFormField from "@/arches_component_lab/generic/GenericFormField.vue";

import { formatDate } from "@/arches_component_lab/datatypes/date/utils.ts";

import type { FormFieldResolverOptions } from "@primevue/forms";
import type { DateDatatypeCardXNodeXWidgetData } from "@/arches_component_lab/datatypes/date/types.ts";
import type { NodeData } from "@/arches_component_lab/types.ts";

const { value, nodeAlias, cardXNodeXWidgetData } = defineProps<{
    value: NodeData | null | undefined;
    nodeAlias: string;
    cardXNodeXWidgetData: DateDatatypeCardXNodeXWidgetData;
}>();

defineEmits(["update:isDirty", "update:value"]);

const shouldShowTime = ref(false);
const dateFormat = ref();

watchEffect(() => {
    const convertedDateFormat =
        convertISO8601DatetimeFormatToPrimevueDatetimeFormat(
            cardXNodeXWidgetData.config.dateFormat,
        );

    dateFormat.value = convertedDateFormat.dateFormat;
    shouldShowTime.value = convertedDateFormat.shouldShowTime;
});

function resolver(event: FormFieldResolverOptions) {
    return {
        values: {
            [nodeAlias]: formatDate(event.value, dateFormat.value) ?? null,
        },
    };
}
</script>

<template>
    <GenericFormField
        v-bind="$attrs"
        :node-alias="nodeAlias"
        :initial-value="value?.interchange_value"
        :resolver="resolver"
    >
        <DatePicker
            icon-display="input"
            :date-format="dateFormat"
            :fluid="true"
            :show-time="shouldShowTime"
            :show-seconds="shouldShowTime"
            :show-icon="true"
            @keydown.enter.prevent
        />
    </GenericFormField>
</template>
