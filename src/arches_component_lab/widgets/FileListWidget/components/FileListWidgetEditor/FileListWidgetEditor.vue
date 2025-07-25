<script setup lang="ts">
import { onMounted, ref } from "vue";

import FileUpload from "primevue/fileupload";

import GenericFormField from "@/arches_component_lab/generics/GenericFormField.vue";
import FileList from "@/arches_component_lab/widgets/FileListWidget/components/FileListWidgetEditor/components/FileList.vue";
import FileDropZone from "@/arches_component_lab/widgets/FileListWidget/components/FileListWidgetEditor/components/FileDropZone.vue";

import type { FormFieldResolverOptions } from "@primevue/forms";
import type {
    FileListCardXNodeXWidgetData,
    FileListValue,
    FileReference,
} from "@/arches_component_lab/datatypes/file-list/types.ts";
import type {
    FileData,
    PrimeVueFile,
} from "@/arches_component_lab/widgets/FileListWidget/types.ts";

const props = defineProps<{
    value: FileListValue;
    nodeAlias: string;
    cardXNodeXWidgetData: FileListCardXNodeXWidgetData;
}>();

const savedFiles = ref<FileReference[]>([]);
const pendingFiles = ref<FileData[]>([]);

const allowedFileTypes = ref();
const currentValues = ref();

onMounted(() => {
    const acceptedFiles = props.cardXNodeXWidgetData.config.acceptedFiles;
    allowedFileTypes.value = acceptedFiles != "" ? acceptedFiles : null;

    if (props.value) {
        currentValues.value = props.value.node_value;

        if (props.value.node_value) {
            savedFiles.value = props.value.node_value.map((file) => {
                return {
                    ...file,
                    node_id: props.cardXNodeXWidgetData.node.nodeid,
                };
            });
        } else {
            savedFiles.value = [];
        }
    }
});

function onSelect(event: { files: PrimeVueFile[] }, field: unknown): void {
    pendingFiles.value = event.files.map((file) => ({
        name: file.name,
        size: file.size,
        type: file.type,
        url: file.objectURL,
        file: file,
        node_id: props.cardXNodeXWidgetData.node.nodeid,
    }));

    (field as { onInput: (value: unknown) => void }).onInput({
        value: [...savedFiles.value, ...pendingFiles.value],
    });
}

function onRemovePendingFile(
    field: unknown,
    fileIndex: number,
    removeFileCallback: (index: number) => void,
): void {
    removeFileCallback(fileIndex);
    pendingFiles.value.splice(fileIndex, 1);

    (field as { onInput: (value: unknown) => void }).onInput({
        value: [...savedFiles.value, ...pendingFiles.value],
    });
}

function onRemoveSavedFile(field: unknown, fileIndex: number): void {
    savedFiles.value.splice(fileIndex, 1);

    (field as { onInput: (value: unknown) => void }).onInput({
        value: [...savedFiles.value, ...pendingFiles.value],
    });
}

function transformValueForForm(event: FormFieldResolverOptions) {
    return {
        display_value: event.value,
        node_value: event.value,
        details: [],
    };
}
</script>

<template>
    <GenericFormField
        v-bind="$attrs"
        :node-alias="nodeAlias"
        :transform-value-for-form="transformValueForForm"
    >
        <template #default="$field">
            <FileUpload
                :accept="allowedFileTypes"
                :name="nodeAlias"
                :model-value="value.node_value"
                :multiple="true"
                :show-cancel-button="false"
                :show-upload-button="false"
                :with-credentials="true"
                :custom-upload="true"
                @select="onSelect($event, $field)"
            >
                <template #content="{ removeFileCallback }">
                    <FileDropZone />

                    <FileList
                        :files="pendingFiles as unknown as FileReference[]"
                        @remove="
                            (_fileReference, fileIndex) =>
                                onRemovePendingFile(
                                    $field,
                                    fileIndex,
                                    removeFileCallback,
                                )
                        "
                    />

                    <FileList
                        :files="savedFiles"
                        @remove="
                            (_fileReference, fileIndex) =>
                                onRemoveSavedFile($field, fileIndex)
                        "
                    />
                </template>
            </FileUpload>
        </template>
    </GenericFormField>
</template>

<style scoped>
:deep(.p-fileupload-header) {
    display: none;
}
:deep(.p-fileupload-content) {
    padding: 0;
}
</style>
