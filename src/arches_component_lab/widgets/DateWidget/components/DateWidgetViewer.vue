<script setup lang="ts">
import DatePicker from "primevue/datepicker";

const props = defineProps<{
    initialValue: string | undefined;
    configuration: any;
}>();
</script>

<template>
    <DatePicker
        v-model="props.initialValue"
        :date-format="configuration.dateFormat"
        disabled
    />
</template>
