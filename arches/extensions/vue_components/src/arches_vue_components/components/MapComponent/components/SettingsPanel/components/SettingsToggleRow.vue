<script setup lang="ts">
import { useId } from "vue";

import ToggleSwitch from "openvue/toggleswitch";

const UPDATE_MODEL_VALUE_EVENT = "update:modelValue" as const;

const {
    modelValue,
    label,
    description = undefined,
} = defineProps<{
    modelValue: boolean;
    label: string;
    description?: string;
}>();

const emit = defineEmits<{
    (event: typeof UPDATE_MODEL_VALUE_EVENT, value: boolean): void;
}>();

const inputId = useId();
</script>

<template>
    <label
        class="settings-toggle-row"
        :for="inputId"
    >
        <span class="settings-toggle-text">
            <span class="settings-toggle-label">{{ label }}</span>
            <span
                v-if="description"
                class="settings-toggle-description"
            >
                {{ description }}
            </span>
        </span>
        <ToggleSwitch
            class="settings-toggle-switch"
            :model-value="modelValue"
            :input-id="inputId"
            @update:model-value="emit(UPDATE_MODEL_VALUE_EVENT, $event)"
        />
    </label>
</template>

<style scoped>
.settings-toggle-row {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1.6rem;
    margin: 0;
    cursor: pointer;
}

.settings-toggle-switch {
    flex: 0 0 auto;
}

.settings-toggle-text {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
}

.settings-toggle-label {
    color: var(--p-text-color);
    font-size: 1.35rem;
    font-weight: 600;
}

.settings-toggle-description {
    color: var(--p-text-muted-color);
    font-size: 1.2rem;
    font-weight: 400;
    line-height: 1.4;
}
</style>
