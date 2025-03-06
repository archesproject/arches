<script setup lang="ts">
import DatePicker from "primevue/datepicker";

const props = defineProps<{
    value: string | null | undefined;
    widgetData: {
        config: {
            dateFormat: string;
        };
    };
}>();
</script>

<template>
    <DatePicker
        v-model="
            /* This compensates for a bug in PrimeVue types */
            props.value as unknown as Date
        "
        :date-format="widgetData.config.dateFormat"
        :disabled="true"
        :fluid="true"
    />
</template>
