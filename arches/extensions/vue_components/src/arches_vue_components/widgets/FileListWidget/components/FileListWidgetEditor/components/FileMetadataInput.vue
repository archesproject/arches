<script setup lang="ts">
import { computed } from "vue";

import InputText from "openvue/inputtext";
import Textarea from "openvue/textarea";

import type { Language } from "@/arches_vue_components/types.ts";

const {
    inputId,
    label,
    language,
    modelValue,
    isMultiline = false,
    isRequired = false,
    helpText = undefined,
    errorText = undefined,
} = defineProps<{
    inputId: string;
    label: string;
    language: Language;
    modelValue: string;
    isMultiline?: boolean;
    isRequired?: boolean;
    helpText?: string;
    errorText?: string;
}>();

const emit = defineEmits<{
    (e: "update:modelValue", value: string): void;
    (e: "blur"): void;
}>();

const helpId = computed(() => `${inputId}-help`);
const errorId = computed(() => `${inputId}-error`);

const describedBy = computed(() => {
    const describingIds = [
        helpText ? helpId.value : undefined,
        errorText ? errorId.value : undefined,
    ].filter(Boolean);
    return describingIds.length ? describingIds.join(" ") : undefined;
});
</script>

<template>
    <div class="file-metadata-field">
        <label :for="inputId">
            {{ label }}
            <span v-if="isRequired">{{ $gettext("(required)") }}</span>
        </label>
        <p
            v-if="helpText"
            :id="helpId"
            class="file-metadata-help"
        >
            {{ helpText }}
        </p>
        <Textarea
            v-if="isMultiline"
            :id="inputId"
            :lang="language.code"
            :dir="language.default_direction"
            :model-value="modelValue"
            :aria-describedby="describedBy"
            rows="2"
            fluid
            @update:model-value="emit('update:modelValue', $event ?? '')"
            @blur="emit('blur')"
        />
        <InputText
            v-else
            :id="inputId"
            :lang="language.code"
            :dir="language.default_direction"
            :model-value="modelValue"
            :aria-required="isRequired ? 'true' : undefined"
            :aria-invalid="errorText ? 'true' : undefined"
            :aria-describedby="describedBy"
            fluid
            @update:model-value="emit('update:modelValue', $event ?? '')"
            @blur="emit('blur')"
        />
        <p
            v-if="errorText"
            :id="errorId"
            class="file-metadata-error"
        >
            {{ errorText }}
        </p>
    </div>
</template>

<style scoped>
.file-metadata-field {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.file-metadata-field label {
    font-weight: 600;
}

.file-metadata-help,
.file-metadata-error {
    margin: 0;
    font-size: 0.875rem;
}

.file-metadata-help {
    color: var(--p-text-muted-color);
}

.file-metadata-error {
    color: var(--p-message-error-simple-color);
}
</style>
