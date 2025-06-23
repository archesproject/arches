<script setup lang="ts">
import DatePicker from "primevue/datepicker";

import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";

const props = defineProps<{
    value: string | null | undefined;
    cardXNodeXWidgetData: CardXNodeXWidget & {
        config: {
            dateFormat: string;
            datePickerDisplayConfiguration: {
                dateFormat: string;
                shouldShowTime: boolean;
            };
        };
    };
}>();
</script>

<template>
    <DatePicker
        v-model="props.value as unknown as Date"
        :disabled="true"
        :date-format="
            props.cardXNodeXWidgetData.config.datePickerDisplayConfiguration
                .dateFormat
        "
        :fluid="true"
        :show-time="
            props.cardXNodeXWidgetData.config.datePickerDisplayConfiguration
                .shouldShowTime
        "
        :show-seconds="
            props.cardXNodeXWidgetData.config.datePickerDisplayConfiguration
                .shouldShowTime
        "
    />
</template>
