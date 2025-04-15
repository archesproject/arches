<script setup lang="ts">
import DatePicker from "primevue/datepicker";

const props = defineProps<{
    initialValue: string | null | undefined;
    widgetData: {
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
        v-model="props.initialValue as unknown as Date"
        :disabled="true"
        :date-format="
            props.widgetData.config.datePickerDisplayConfiguration.dateFormat
        "
        :fluid="true"
        :show-time="
            props.widgetData.config.datePickerDisplayConfiguration
                .shouldShowTime
        "
        :show-seconds="
            props.widgetData.config.datePickerDisplayConfiguration
                .shouldShowTime
        "
    />
</template>
