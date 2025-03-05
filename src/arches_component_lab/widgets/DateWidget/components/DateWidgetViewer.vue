<script setup lang="ts">
import DatePicker from "primevue/datepicker";

const props = defineProps<{
    value: string | Date | undefined;
    widgetData: {
        config: {
            dateFormat: string;
        }
    };
}>();
</script>

<template>
    <DatePicker
        v-model="props.value as Date"
        :date-format="widgetData.config.dateFormat"
        :disabled="true"
        :fluid="true"
    />
</template>
