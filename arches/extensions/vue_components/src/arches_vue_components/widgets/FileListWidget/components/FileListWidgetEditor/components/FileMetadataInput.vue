<script setup lang="ts">
import { computed, ref } from "vue";

import Button from "openvue/button";
import InputText from "openvue/inputtext";
import Select from "openvue/select";
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
    selectableLanguages = [],
    languageToggleAriaLabel = undefined,
} = defineProps<{
    inputId: string;
    label: string;
    language: Language;
    modelValue: string;
    isMultiline?: boolean;
    isRequired?: boolean;
    helpText?: string;
    errorText?: string;
    selectableLanguages?: Language[];
    languageToggleAriaLabel?: string;
}>();

const emit = defineEmits<{
    (e: "update:modelValue", value: string): void;
    (e: "update:language", languageCode: string): void;
    (e: "blur"): void;
}>();

const isLanguagePanelOpen = ref(false);

const helpId = computed(() => `${inputId}-help`);
const errorId = computed(() => `${inputId}-error`);
const languagePanelId = computed(() => `${inputId}-language-panel`);
const languageLabelId = computed(() => `${inputId}-language-label`);

const shouldShowLanguageToggle = computed(() => selectableLanguages.length > 1);

const describedBy = computed(() => {
    const describingIds = [
        helpText ? helpId.value : undefined,
        errorText ? errorId.value : undefined,
    ].filter(Boolean);
    return describingIds.length ? describingIds.join(" ") : undefined;
});

function formatLanguageOption(option: Language): string {
    return `${option.name} (${option.code})`;
}
</script>

<template>
    <div class="file-metadata-field">
        <div class="file-metadata-label-row">
            <label
                :for="inputId"
                class="file-metadata-label"
            >
                {{ label }}
                <span v-if="isRequired">{{ $gettext("(required)") }}</span>
            </label>
            <Button
                v-if="shouldShowLanguageToggle"
                class="metadata-language-toggle"
                :icon="
                    isLanguagePanelOpen
                        ? 'pi pi-chevron-down'
                        : 'pi pi-chevron-right'
                "
                :label="$gettext('Languages')"
                :aria-label="languageToggleAriaLabel"
                :aria-expanded="isLanguagePanelOpen"
                :aria-controls="languagePanelId"
                size="small"
                text
                @click="isLanguagePanelOpen = !isLanguagePanelOpen"
            />
        </div>
        <div
            v-if="shouldShowLanguageToggle"
            v-show="isLanguagePanelOpen"
            :id="languagePanelId"
            class="metadata-language-panel"
        >
            <label :id="languageLabelId">{{ $gettext("Language") }}</label>
            <Select
                :model-value="language.code"
                :options="selectableLanguages"
                :option-label="formatLanguageOption"
                option-value="code"
                :aria-labelledby="languageLabelId"
                fluid
                @update:model-value="emit('update:language', $event)"
            />
        </div>
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
    width: 100%;
}

.file-metadata-label-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.file-metadata-label {
    flex: 1 1 auto;
    font-weight: 600;
}

.metadata-language-toggle {
    flex: 0 0 auto;
}

.metadata-language-panel {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    padding: 0.75rem;
    border: 1px solid var(--p-content-border-color);
    border-radius: var(--p-content-border-radius);
    background: var(--p-content-background);
}

.metadata-language-panel label {
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
