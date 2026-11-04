<script setup lang="ts">
import { computed, ref, useId } from "vue";
import { useGettext } from "vue3-gettext";

import Image from "openvue/image";
import Button from "openvue/button";
import Select from "openvue/select";

import FileMetadataInput from "@/arches_vue_components/widgets/FileListWidget/components/FileListWidgetEditor/components/FileMetadataInput.vue";

import {
    ADDITIONAL_FILE_METADATA_FIELDS,
    FILE_METADATA_FIELDS,
    PRIMARY_FILE_METADATA_FIELDS,
    REMOVE,
    UPDATE_METADATA,
} from "@/arches_vue_components/datatypes/file-list/constants.ts";
import {
    getFileAltText,
    getLocalizedValue,
    hasAnyAltText,
    setLocalizedValue,
} from "@/arches_vue_components/datatypes/file-list/utils.ts";

import type { Language } from "@/arches_vue_components/types.ts";
import type { LanguageValue } from "@/arches_vue_components/datatypes/string/types.ts";
import type {
    FileMetadataField,
    FileReference,
} from "@/arches_vue_components/datatypes/file-list/types.ts";

const {
    files,
    languages = [],
    defaultMetadataLanguage = undefined,
    shouldShowLanguageSelect = false,
    visibleMetadataFields = FILE_METADATA_FIELDS,
    isAltTextRequired = false,
} = defineProps<{
    files: FileReference[];
    languages?: Language[];
    defaultMetadataLanguage?: Language;
    shouldShowLanguageSelect?: boolean;
    visibleMetadataFields?: readonly FileMetadataField[];
    isAltTextRequired?: boolean;
}>();

const emit = defineEmits<{
    (
        e: typeof REMOVE,
        fileReference: FileReference,
        fileIndex: number,
        event: Event,
    ): void;
    (
        e: typeof UPDATE_METADATA,
        fileIndex: number,
        field: FileMetadataField,
        localizedValue: Record<string, LanguageValue>,
    ): void;
}>();

const { $gettext } = useGettext();

const listId = useId();
const touchedAltTextKeys = ref(new Set<string>());
const expandedFileKeys = ref(new Set<string>());
const selectedLanguageCodes = ref(new Map<string, string>());

const metadataFieldLabels = computed<Record<FileMetadataField, string>>(() => ({
    altText: $gettext("Alternative text"),
    title: $gettext("Title"),
    description: $gettext("Description"),
    attribution: $gettext("Attribution"),
}));

const primaryFields = computed(() =>
    PRIMARY_FILE_METADATA_FIELDS.filter((field) =>
        visibleMetadataFields.includes(field),
    ),
);

const additionalFields = computed(() =>
    ADDITIONAL_FILE_METADATA_FIELDS.filter((field) =>
        visibleMetadataFields.includes(field),
    ),
);

function getFileKey(fileReference: FileReference): string {
    return fileReference.file_id ?? fileReference.url;
}

function getFieldId(fileIndex: number, field: string): string {
    return `${listId}-${fileIndex}-${field}`;
}

function getFileLanguage(fileReference: FileReference): Language | undefined {
    const selectedCode = selectedLanguageCodes.value.get(
        getFileKey(fileReference),
    );
    return (
        languages.find((language) => language.code === selectedCode) ??
        defaultMetadataLanguage
    );
}

function onSelectFileLanguage(
    fileReference: FileReference,
    languageCode: string,
) {
    selectedLanguageCodes.value.set(getFileKey(fileReference), languageCode);
}

function isExpanded(fileReference: FileReference): boolean {
    return expandedFileKeys.value.has(getFileKey(fileReference));
}

function toggleExpanded(fileReference: FileReference) {
    const fileKey = getFileKey(fileReference);
    if (!expandedFileKeys.value.delete(fileKey)) {
        expandedFileKeys.value.add(fileKey);
    }
}

function markAltTextTouched(fileReference: FileReference) {
    touchedAltTextKeys.value.add(getFileKey(fileReference));
}

function getHelpText(field: FileMetadataField): string | undefined {
    if (field !== "altText") {
        return undefined;
    }
    return $gettext("Describe the image for people who cannot see it.");
}

function getErrorText(
    fileReference: FileReference,
    field: FileMetadataField,
): string | undefined {
    const shouldShowAltTextError =
        field === "altText" &&
        isAltTextRequired &&
        touchedAltTextKeys.value.has(getFileKey(fileReference)) &&
        !hasAnyAltText(fileReference);

    if (!shouldShowAltTextError) {
        return undefined;
    }
    return $gettext(
        "Enter alternative text for %{fileName}.",
        { fileName: fileReference.name },
        true,
    );
}

function onBlurField(fileReference: FileReference, field: FileMetadataField) {
    if (field === "altText") {
        markAltTextTouched(fileReference);
    }
}

function onUpdateField(
    fileReference: FileReference,
    fileIndex: number,
    field: FileMetadataField,
    value: string,
) {
    const language = getFileLanguage(fileReference);
    if (!language) {
        return;
    }
    emit(
        UPDATE_METADATA,
        fileIndex,
        field,
        setLocalizedValue(fileReference[field], language, value),
    );
}
</script>

<template>
    <ul
        v-if="files.length"
        class="file-list"
        @click.stop
    >
        <li
            v-for="(fileReference, fileIndex) in files"
            :key="getFileKey(fileReference)"
            class="file-list-item"
        >
            <div
                class="file-summary"
                @click.prevent
            >
                <Image
                    image-class="image-list-image"
                    :src="fileReference.url"
                    :alt="
                        getFileAltText(
                            fileReference,
                            getFileLanguage(fileReference)?.code ?? null,
                        )
                    "
                />
                <span class="file-name">{{ fileReference.name }}</span>
                <Button
                    icon="pi pi-times"
                    severity="danger"
                    outlined
                    rounded
                    class="delete-button"
                    :aria-label="
                        $gettext(
                            'Remove %{fileName}',
                            { fileName: fileReference.name },
                            true,
                        )
                    "
                    @click="
                        (event) => emit(REMOVE, fileReference, fileIndex, event)
                    "
                />
            </div>

            <div
                v-if="shouldShowLanguageSelect && languages.length > 1"
                class="file-metadata-language"
            >
                <label :id="getFieldId(fileIndex, 'language')">
                    {{ $gettext("Language of file details") }}
                </label>
                <Select
                    :model-value="getFileLanguage(fileReference)?.code"
                    :options="languages"
                    option-label="name"
                    option-value="code"
                    :aria-labelledby="getFieldId(fileIndex, 'language')"
                    @update:model-value="
                        onSelectFileLanguage(fileReference, $event)
                    "
                />
            </div>

            <div
                v-if="getFileLanguage(fileReference)"
                class="file-metadata"
            >
                <FileMetadataInput
                    v-for="field in primaryFields"
                    :key="field"
                    :input-id="getFieldId(fileIndex, field)"
                    :label="metadataFieldLabels[field]"
                    :language="getFileLanguage(fileReference)!"
                    :model-value="
                        getLocalizedValue(
                            fileReference[field],
                            getFileLanguage(fileReference)!.code,
                        )
                    "
                    :is-required="field === 'altText' && isAltTextRequired"
                    :help-text="getHelpText(field)"
                    :error-text="getErrorText(fileReference, field)"
                    @update:model-value="
                        onUpdateField(fileReference, fileIndex, field, $event)
                    "
                    @blur="onBlurField(fileReference, field)"
                />

                <template v-if="additionalFields.length">
                    <Button
                        class="additional-metadata-toggle"
                        :icon="
                            isExpanded(fileReference)
                                ? 'pi pi-chevron-down'
                                : 'pi pi-chevron-right'
                        "
                        :label="$gettext('Additional metadata')"
                        :aria-expanded="isExpanded(fileReference)"
                        :aria-controls="getFieldId(fileIndex, 'additional')"
                        text
                        @click="toggleExpanded(fileReference)"
                    />
                    <div
                        v-show="isExpanded(fileReference)"
                        :id="getFieldId(fileIndex, 'additional')"
                        class="file-metadata"
                    >
                        <FileMetadataInput
                            v-for="field in additionalFields"
                            :key="field"
                            :input-id="getFieldId(fileIndex, field)"
                            :label="metadataFieldLabels[field]"
                            :language="getFileLanguage(fileReference)!"
                            :model-value="
                                getLocalizedValue(
                                    fileReference[field],
                                    getFileLanguage(fileReference)!.code,
                                )
                            "
                            :is-multiline="field === 'description'"
                            @update:model-value="
                                onUpdateField(
                                    fileReference,
                                    fileIndex,
                                    field,
                                    $event,
                                )
                            "
                        />
                    </div>
                </template>
            </div>
        </li>
    </ul>
</template>

<style scoped>
.file-list {
    list-style: none;
    margin: 0;
    padding: 0;
}

.file-list-item {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding-block: 0.5rem;
}

.file-summary {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    width: 100%;
}

:deep(.image-list-image) {
    flex: 1 1 auto;
    max-width: 100%;
    height: auto;
}

.file-name {
    flex: 1 1 auto;
    overflow-wrap: anywhere;
}

.delete-button {
    flex: 0 0 auto;
}

.file-metadata-language {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.file-metadata-language label {
    font-weight: 600;
}

.file-metadata {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.additional-metadata-toggle {
    align-self: flex-start;
}
</style>
