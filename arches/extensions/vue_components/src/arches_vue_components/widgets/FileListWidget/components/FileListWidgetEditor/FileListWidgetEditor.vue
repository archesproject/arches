<script setup lang="ts">
import { computed, onMounted, ref, watchEffect } from "vue";

import FileUpload from "openvue/fileupload";

import FileList from "@/arches_vue_components/widgets/FileListWidget/components/FileListWidgetEditor/components/FileList.vue";
import FileDropZone from "@/arches_vue_components/widgets/FileListWidget/components/FileListWidgetEditor/components/FileDropZone.vue";

import { useLanguageStore } from "@/arches_vue_components/stores/useLanguageStore.ts";
import { FILE_METADATA_FIELDS } from "@/arches_vue_components/datatypes/file-list/constants.ts";
import {
    buildEmptyFileMetadata,
    buildFileListAliasedNodeData,
} from "@/arches_vue_components/datatypes/file-list/utils.ts";

import type { LanguageValue } from "@/arches_vue_components/datatypes/string/types.ts";
import type {
    FileListAliasedNodeData,
    FileListCardXNodeXWidgetData,
    FileMetadataField,
    FileReference,
} from "@/arches_vue_components/datatypes/file-list/types.ts";
import type {
    FileData,
    OpenVueFile,
} from "@/arches_vue_components/widgets/FileListWidget/types.ts";

const {
    aliasedNodeData,
    cardXNodeXWidgetData = undefined,
    shouldShowMetadataLanguageSelect = false,
    visibleMetadataFields = FILE_METADATA_FIELDS,
} = defineProps<{
    aliasedNodeData: FileListAliasedNodeData | null;
    cardXNodeXWidgetData?: FileListCardXNodeXWidgetData;
    shouldShowMetadataLanguageSelect?: boolean;
    visibleMetadataFields?: readonly FileMetadataField[];
}>();

const emit = defineEmits<{
    (
        event: "update:aliasedNodeData",
        updatedValue: FileListAliasedNodeData,
    ): void;
}>();

const fileUploadRef = ref<InstanceType<typeof FileUpload> | null>(null);

const languageStore = useLanguageStore();

onMounted(async () => {
    await languageStore.fetchAllLanguages();
});

const requestLanguage = computed(() =>
    languageStore.languages.find(
        (language) => language.code === languageStore.requestLanguageCode,
    ),
);

const isAltTextRequired = computed(() =>
    Boolean(cardXNodeXWidgetData?.node.config?.imagesOnly),
);

const savedFiles = ref<FileReference[]>([]);
const pendingFiles = ref<FileData[]>([]);
const maxFiles = ref(
    (cardXNodeXWidgetData?.node.config.maxFiles ?? 0) as number,
);

const isDisabled = computed(() => {
    const totalFiles = savedFiles.value.length + pendingFiles.value.length;
    return maxFiles.value ? maxFiles.value <= totalFiles : false;
});

const acceptedFileTypes = computed(() => {
    const fileTypes: string[] = [];
    const acceptedFiles = cardXNodeXWidgetData?.config.acceptedFiles;
    const imagesOnly = cardXNodeXWidgetData?.node.config?.imagesOnly;

    if (acceptedFiles) {
        fileTypes.push(...acceptedFiles.split(","));
    }
    if (imagesOnly) {
        fileTypes.push("image/*");
    }

    return fileTypes;
});

watchEffect(() => {
    const nodeId = cardXNodeXWidgetData?.node.nodeid ?? "";

    if (!aliasedNodeData?.node_value) {
        savedFiles.value = [];
        pendingFiles.value = [];
        return;
    }

    // Entries still carrying a raw File aren't saved yet -- route to pendingFiles.
    const nextSavedFiles: FileReference[] = [];
    const nextPendingFiles: FileData[] = [];

    for (const fileReference of aliasedNodeData.node_value) {
        const fileReferenceWithNodeId = { ...fileReference, node_id: nodeId };

        if ("file" in fileReference && fileReference.file instanceof File) {
            nextPendingFiles.push(
                fileReferenceWithNodeId as unknown as FileData,
            );
        } else {
            nextSavedFiles.push(fileReferenceWithNodeId as FileReference);
        }
    }

    savedFiles.value = nextSavedFiles;
    pendingFiles.value = nextPendingFiles;
});

function emitUpdatedValue() {
    const allFiles = [
        ...savedFiles.value,
        ...pendingFiles.value,
    ] as FileReference[];
    emit("update:aliasedNodeData", buildFileListAliasedNodeData(allFiles));
}

function onSelect(event: { files: OpenVueFile[] }): void {
    // event.files holds every pending file, not just the new ones, so keep
    // the metadata already entered for files that were selected earlier.
    pendingFiles.value = event.files.map((file) => {
        const existingPendingFile = pendingFiles.value.find(
            (pendingFile) => pendingFile.file === file,
        );
        return {
            ...buildEmptyFileMetadata(languageStore.languages),
            ...existingPendingFile,
            name: file.name,
            size: file.size,
            type: file.type,
            url: file.objectURL,
            file: file,
            node_id: cardXNodeXWidgetData?.node.nodeid ?? "",
        };
    });

    emitUpdatedValue();
}

function onUpdatePendingFileMetadata(
    fileIndex: number,
    field: FileMetadataField,
    localizedValue: Record<string, LanguageValue>,
): void {
    pendingFiles.value[fileIndex] = {
        ...pendingFiles.value[fileIndex],
        [field]: localizedValue,
    };
    emitUpdatedValue();
}

function onUpdateSavedFileMetadata(
    fileIndex: number,
    field: FileMetadataField,
    localizedValue: Record<string, LanguageValue>,
): void {
    savedFiles.value[fileIndex] = {
        ...savedFiles.value[fileIndex],
        [field]: localizedValue,
    };
    emitUpdatedValue();
}

function onRemovePendingFile(
    fileIndex: number,
    removeFileCallback: (index: number) => void,
): void {
    removeFileCallback(fileIndex);
    pendingFiles.value.splice(fileIndex, 1);

    emitUpdatedValue();
}

function onRemoveSavedFile(fileIndex: number): void {
    savedFiles.value.splice(fileIndex, 1);
    emitUpdatedValue();
}

function openFileChooser(): void {
    // @ts-expect-error FileUpload does not have a type definition for $el
    const rootElement = fileUploadRef.value?.$el;
    rootElement?.querySelector('input[type="file"]')?.click();
}
</script>

<template>
    <FileUpload
        ref="fileUploadRef"
        :accept="
            acceptedFileTypes.length ? acceptedFileTypes.join(',') : undefined
        "
        :model-value="aliasedNodeData?.node_value"
        :multiple="maxFiles && maxFiles > 1 ? true : false"
        :show-cancel-button="false"
        :show-upload-button="false"
        :with-credentials="true"
        :custom-upload="true"
        @select="onSelect($event)"
    >
        <template #content="{ removeFileCallback }">
            <FileDropZone
                :card-x-node-x-widget-data="cardXNodeXWidgetData"
                :open-file-chooser="openFileChooser"
                :is-disabled="isDisabled"
                :accepted-file-types="acceptedFileTypes"
            />

            <FileList
                :files="pendingFiles as unknown as FileReference[]"
                :languages="languageStore.languages"
                :default-metadata-language="requestLanguage"
                :should-show-language-select="shouldShowMetadataLanguageSelect"
                :visible-metadata-fields="visibleMetadataFields"
                :is-alt-text-required="isAltTextRequired"
                @remove="
                    (_fileReference, fileIndex) =>
                        onRemovePendingFile(fileIndex, removeFileCallback)
                "
                @update:metadata="onUpdatePendingFileMetadata"
            />

            <FileList
                :files="savedFiles"
                :languages="languageStore.languages"
                :default-metadata-language="requestLanguage"
                :should-show-language-select="shouldShowMetadataLanguageSelect"
                :visible-metadata-fields="visibleMetadataFields"
                :is-alt-text-required="isAltTextRequired"
                @remove="
                    (_fileReference, fileIndex) => onRemoveSavedFile(fileIndex)
                "
                @update:metadata="onUpdateSavedFileMetadata"
            />
        </template>
    </FileUpload>
</template>

<style scoped>
:deep(.p-fileupload-header) {
    display: none;
}
:deep(.p-fileupload-content) {
    padding: 0;
}
</style>
