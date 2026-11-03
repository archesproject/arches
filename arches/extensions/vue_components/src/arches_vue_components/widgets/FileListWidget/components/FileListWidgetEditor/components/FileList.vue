<script setup lang="ts">
import { computed, ref, useId } from "vue";
import { useGettext } from "vue3-gettext";

import Image from "openvue/image";
import Button from "openvue/button";

import FileMetadataInput from "@/arches_vue_components/widgets/FileListWidget/components/FileListWidgetEditor/components/FileMetadataInput.vue";

import {
    ADDITIONAL_FILE_METADATA_FIELDS,
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
    metadataLanguage = undefined,
    isAltTextRequired = false,
} = defineProps<{
    files: FileReference[];
    metadataLanguage?: Language;
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

const metadataFieldLabels = computed<Record<FileMetadataField, string>>(() => ({
    altText: $gettext("Alternative text"),
    title: $gettext("Title"),
    description: $gettext("Description"),
    attribution: $gettext("Attribution"),
}));

function getFileKey(fileReference: FileReference): string {
    return fileReference.file_id ?? fileReference.url;
}

function getFieldId(fileIndex: number, field: string): string {
    return `${listId}-${fileIndex}-${field}`;
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
    if (!metadataLanguage) {
        return;
    }
    emit(
        UPDATE_METADATA,
        fileIndex,
        field,
        setLocalizedValue(fileReference[field], metadataLanguage, value),
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
                            metadataLanguage?.code ?? null,
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
                v-if="metadataLanguage"
                class="file-metadata"
            >
                <FileMetadataInput
                    v-for="field in PRIMARY_FILE_METADATA_FIELDS"
                    :key="field"
                    :input-id="getFieldId(fileIndex, field)"
                    :label="metadataFieldLabels[field]"
                    :language="metadataLanguage"
                    :model-value="
                        getLocalizedValue(
                            fileReference[field],
                            metadataLanguage.code,
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
                        v-for="field in ADDITIONAL_FILE_METADATA_FIELDS"
                        :key="field"
                        :input-id="getFieldId(fileIndex, field)"
                        :label="metadataFieldLabels[field]"
                        :language="metadataLanguage"
                        :model-value="
                            getLocalizedValue(
                                fileReference[field],
                                metadataLanguage.code,
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

.file-metadata {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.additional-metadata-toggle {
    align-self: flex-start;
}
</style>
