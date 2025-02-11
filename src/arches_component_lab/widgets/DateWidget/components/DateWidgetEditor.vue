<script setup lang="ts">
import { ref, computed } from "vue";

import DatePicker from "primevue/datepicker";

const props = defineProps<{
    initialValue: any | undefined;
    configuration: any;
}>();

const internalValue = ref(props.initialValue);

const rawValue = computed(() => parseDate(internalValue.value));
const isDirty = computed(() => rawValue.value !== props.initialValue);

defineExpose({
    rawValue,
    isDirty,
});

// Datepicker returns date object, which needs to be parsed to post back
// https://github.com/primefaces/primevue/issues/6278
function parseDate(date: unknown): string | null {
    if (date) {
        return new Date(date as string).toISOString().split("T")[0];
    }
    return null;
}
</script>

<template>
    <DatePicker
        v-model="internalValue"
        style="display: flex"
        icon-display="input"
        :date-format="configuration.dateFormat"
        :show-icon="true"
        :fluid="true"
        :manual-input="true"
    />
</template>
