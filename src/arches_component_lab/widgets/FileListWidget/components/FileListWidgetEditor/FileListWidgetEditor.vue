<script setup lang="ts">
import { ref, watchEffect } from "vue";

import FileUpload from "primevue/fileupload";

import FileList from "@/arches_component_lab/widgets/FileListWidget/components/FileListWidgetEditor/components/FileList.vue";
import FileDropZone from "@/arches_component_lab/widgets/FileListWidget/components/FileListWidgetEditor/components/FileDropZone.vue";

import type {
    FileListCardXNodeXWidgetData,
    FileListValue,
    FileReference,
} from "@/arches_component_lab/datatypes/file-list/types.ts";
import type {
    FileData,
    PrimeVueFile,
} from "@/arches_component_lab/widgets/FileListWidget/types.ts";

const { aliasedNodeData, nodeAlias, cardXNodeXWidgetData } = defineProps<{
    aliasedNodeData: FileListValue;
    nodeAlias: string;
    cardXNodeXWidgetData: FileListCardXNodeXWidgetData;
}>();

const emit = defineEmits<{
    (event: "update:value", updatedValue: FileListValue): void;
}>();

const fileUploadRef = ref<InstanceType<typeof FileUpload> | null>(null);

const savedFiles = ref<FileReference[]>([]);
const pendingFiles = ref<FileData[]>([]);

const allowedFileTypes = ref();
const currentValues = ref();

watchEffect(() => {
    const acceptedFiles = cardXNodeXWidgetData.config.acceptedFiles;
    allowedFileTypes.value = acceptedFiles != "" ? acceptedFiles : null;

    if (aliasedNodeData) {
        currentValues.value = aliasedNodeData.node_value;

        if (aliasedNodeData.node_value) {
            savedFiles.value = aliasedNodeData.node_value.map((file) => {
                return {
                    ...file,
                    node_id: cardXNodeXWidgetData.node.nodeid,
                };
            });
        } else {
            savedFiles.value = [];
        }
    }
});

function emitUpdatedValue() {
    const allFiles = [
        ...savedFiles.value,
        ...pendingFiles.value,
    ] as FileReference[];

    emit("update:value", {
        display_value: JSON.stringify(allFiles),
        node_value: allFiles,
        details: [],
    });
}

function onSelect(event: { files: PrimeVueFile[] }): void {
    pendingFiles.value = event.files.map((file) => ({
        name: file.name,
        size: file.size,
        type: file.type,
        url: file.objectURL,
        file: file,
        node_id: cardXNodeXWidgetData.node.nodeid,
    }));

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
        :accept="allowedFileTypes"
        :name="nodeAlias"
        :model-value="aliasedNodeData.node_value"
        :multiple="true"
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
            />

            <FileList
                :files="pendingFiles as unknown as FileReference[]"
                @remove="
                    (_fileReference, fileIndex) =>
                        onRemovePendingFile(fileIndex, removeFileCallback)
                "
            />

            <FileList
                :files="savedFiles"
                @remove="
                    (_fileReference, fileIndex) => onRemoveSavedFile(fileIndex)
                "
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
