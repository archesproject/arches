<script setup lang="ts">
import { computed, ref } from "vue";
import { useGettext } from "vue3-gettext";

import InputText from "openvue/inputtext";
import Select from "openvue/select";
import Textarea from "openvue/textarea";

import {
    getLocalizedValue,
    setLocalizedValue,
} from "@/arches_vue_components/datatypes/file-list/utils.ts";

import type { Language } from "@/arches_vue_components/types.ts";
import type { LanguageValue } from "@/arches_vue_components/datatypes/string/types.ts";

const {
    inputId,
    label,
    languages,
    defaultLanguage,
    modelValue = undefined,
    isMultiline = false,
    isRequired = false,
    helpText = undefined,
    errorText = undefined,
} = defineProps<{
    inputId: string;
    label: string;
    languages: Language[];
    defaultLanguage: Language;
    modelValue?: Record<string, LanguageValue>;
    isMultiline?: boolean;
    isRequired?: boolean;
    helpText?: string;
    errorText?: string;
}>();

const emit = defineEmits<{
    (
        e: "update:modelValue",
        localizedValue: Record<string, LanguageValue>,
    ): void;
    (e: "blur"): void;
}>();

const { $gettext } = useGettext();

const selectedLanguageCode = ref<string | undefined>(
    getOnlyFilledLanguageCode(),
);

const selectedLanguage = computed(
    () =>
        languages.find(
            (language) => language.code === selectedLanguageCode.value,
        ) ?? defaultLanguage,
);

const inputValue = computed(() =>
    getLocalizedValue(modelValue, selectedLanguage.value.code),
);

const helpId = computed(() => `${inputId}-help`);
const errorId = computed(() => `${inputId}-error`);

const describedBy = computed(() => {
    const describingIds = [
        helpText ? helpId.value : undefined,
        errorText ? errorId.value : undefined,
    ].filter(Boolean);
    return describingIds.length ? describingIds.join(" ") : undefined;
});

const languageSelectAriaLabel = computed(() =>
    $gettext("Language for %{fieldLabel}", { fieldLabel: label }, true),
);

function getOnlyFilledLanguageCode(): string | undefined {
    const filledLanguageCodes = Object.entries(modelValue ?? {})
        .filter(([, languageValue]) => languageValue.value.trim())
        .map(([languageCode]) => languageCode);
    if (filledLanguageCodes.length === 1) {
        return filledLanguageCodes[0];
    }
    return undefined;
}

function formatLanguageOption(option: Language): string {
    return `${option.name}`;
}

function onUpdateInputValue(value: string | undefined) {
    emit(
        "update:modelValue",
        setLocalizedValue(modelValue, selectedLanguage.value, value ?? ""),
    );
}
</script>

<template>
    <div class="file-metadata-field">
        <label
            :for="inputId"
            class="file-metadata-label"
        >
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
        <div class="file-metadata-inputs">
            <Select
                class="file-metadata-language"
                :model-value="selectedLanguage.code"
                :options="languages"
                :option-label="formatLanguageOption"
                option-value="code"
                :aria-label="languageSelectAriaLabel"
                @update:model-value="selectedLanguageCode = $event"
            />
            <Textarea
                v-if="isMultiline"
                :id="inputId"
                :lang="selectedLanguage.code"
                :dir="selectedLanguage.default_direction"
                :model-value="inputValue"
                :aria-describedby="describedBy"
                rows="3"
                fluid
                @update:model-value="onUpdateInputValue"
                @blur="emit('blur')"
            />
            <InputText
                v-else
                :id="inputId"
                :lang="selectedLanguage.code"
                :dir="selectedLanguage.default_direction"
                :model-value="inputValue"
                :aria-required="isRequired ? 'true' : undefined"
                :aria-invalid="errorText ? 'true' : undefined"
                :aria-describedby="describedBy"
                fluid
                @update:model-value="onUpdateInputValue"
                @blur="emit('blur')"
            />
        </div>
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
    width: 100%;
}

.file-metadata-label {
    font-weight: 600;
}

.file-metadata-inputs {
    display: flex;
    align-items: flex-start;
    column-gap: 0.5rem;
}

.file-metadata-language {
    flex: 0 0 auto;
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
