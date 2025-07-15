<script setup lang="ts">
import { onMounted, ref } from "vue";

import FileUpload from "primevue/fileupload";

import GenericFormField from "@/arches_component_lab/generic/GenericFormField.vue";
import FileList from "@/arches_component_lab/widgets/FileListWidget/components/FileListWidgetEditor/components/FileList.vue";
import FileDropZone from "@/arches_component_lab/widgets/FileListWidget/components/FileListWidgetEditor/components/FileDropZone.vue";

import type { NodeData } from "@/arches_component_lab/types.ts";
import type { FileReference } from "@/arches_component_lab/widgets/types.ts";
import type { FileListCardXNodeXWidgetData } from "@/arches_component_lab/datatypes/file-list/types.ts";

interface FileData {
    name: string;
    size: number;
    type: string;
    url: string;
    file: File;
    node_id: string;
}

type PrimeVueFile = File & { objectURL: string };

const { value, nodeAlias, cardXNodeXWidgetData } = defineProps<{
    value: NodeData | null | undefined;
    nodeAlias: string;
    cardXNodeXWidgetData: FileListCardXNodeXWidgetData;
}>();

const savedFiles = ref<FileReference[]>([]);
const pendingFiles = ref<FileData[]>([]);

const allowedFileTypes = ref();
const currentValues = ref();

onMounted(() => {
    const acceptedFiles = cardXNodeXWidgetData.config.acceptedFiles;
    allowedFileTypes.value = acceptedFiles != "" ? acceptedFiles : null;

    if (value) {
        currentValues.value = value.interchange_value;

        if (value.interchange_value) {
            savedFiles.value = (value.interchange_value as FileReference[]).map(
                (file) => {
                    return {
                        ...file,
                        node_id: cardXNodeXWidgetData.node.nodeid,
                    };
                },
            );
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
        node_id: cardXNodeXWidgetData.node.nodeid,
    }));

    (field as { onInput: (value: unknown) => void }).onInput({
        value: [...savedFiles.value, ...pendingFiles.value],
    });
}
</script>

<template>
    <GenericFormField
        v-bind="$attrs"
        :node-alias="nodeAlias"
        :initial-value="value?.interchange_value ?? []"
    >
        <template #default="$field">
            <FileUpload
                :accept="allowedFileTypes"
                :name="nodeAlias"
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
                            (_fileReference, fileIndex) => {
                                removeFileCallback(fileIndex);
                                pendingFiles.splice(fileIndex, 1);

                                // @ts-expect-error This is a bug with PrimeVue types
                                $field.onInput({
                                    value: [...savedFiles, ...pendingFiles],
                                });
                            }
                        "
                    />

                    <FileList
                        :files="savedFiles"
                        @remove="
                            (_fileReference, fileIndex) => {
                                savedFiles.splice(fileIndex, 1);

                                // @ts-expect-error This is a bug with PrimeVue types
                                $field.onInput({
                                    value: [...savedFiles, ...pendingFiles],
                                });
                            }
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
