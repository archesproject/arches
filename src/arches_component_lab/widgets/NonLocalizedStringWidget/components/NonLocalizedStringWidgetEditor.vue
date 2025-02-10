<script setup lang="ts">
import { ref, computed } from "vue";

import InputText from "primevue/inputtext";

const props = defineProps<{
    initialValue: string | undefined;
}>();

const rawValue = ref(props.initialValue);
const isDirty = computed(() => rawValue.value !== props.initialValue);

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
