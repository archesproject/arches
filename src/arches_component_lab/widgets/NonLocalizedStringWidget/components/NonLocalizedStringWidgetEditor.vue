<script setup lang="ts">
import { ref, computed, watch } from "vue";

import InputText from "primevue/inputtext";

const props = defineProps<{
    initialValue: string | undefined;
}>();

const rawValue = ref(props.initialValue);
const initialValue = ref(props.initialValue);

const isDirty = computed(() => rawValue.value !== initialValue.value);

watch(
    () => props.initialValue,
    (newVal) => {
        rawValue.value = newVal;
        initialValue.value = newVal;
    },
);

defineExpose({
    rawValue,
    isDirty,
});
</script>

<template>
    <InputText
        v-model="rawValue"
        type="text"
        :fluid="true"
    />
</template>
