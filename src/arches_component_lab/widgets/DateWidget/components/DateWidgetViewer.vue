<script setup lang="ts">
import DatePicker from "primevue/datepicker";

const props = defineProps<{
    value: string | Date | undefined;
    configuration: {
        dateFormat: string;
        graphSlug: string;
        label: string;
        nodeAlias: string;
    };
}>();
</script>

<template>
    <DatePicker
        v-model="props.value as Date"
        :date-format="configuration.dateFormat"
        :disabled="true"
        :fluid="true"
    />
</template>
