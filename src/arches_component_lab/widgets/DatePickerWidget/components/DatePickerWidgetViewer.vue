<script setup lang="ts">
import DatePicker from "primevue/datepicker";

import type { DateDatatypeCardXNodeXWidgetData } from "@/arches_component_lab/datatypes/date/types.ts";
import type { NodeData } from "@/arches_component_lab/types";

defineProps<{
    value: NodeData | null | undefined;
    cardXNodeXWidgetData: DateDatatypeCardXNodeXWidgetData;
}>();
</script>

<template>
    <DatePicker
        v-model="value as unknown as Date"
        :disabled="true"
        :date-format="
            cardXNodeXWidgetData.config.datePickerDisplayConfiguration
                .dateFormat
        "
        :fluid="true"
        :show-time="
            cardXNodeXWidgetData.config.datePickerDisplayConfiguration
                .shouldShowTime
        "
        :show-seconds="
            cardXNodeXWidgetData.config.datePickerDisplayConfiguration
                .shouldShowTime
        "
    />
</template>
