<script setup lang="ts">
import { computed, onMounted } from "vue";

import FileListWidgetViewer from "@/arches_vue_components/widgets/FileListWidget/components/FileListWidgetViewer.vue";
import FileListWidgetEditor from "@/arches_vue_components/widgets/FileListWidget/components/FileListWidgetEditor/FileListWidgetEditor.vue";

import { EDIT, VIEW } from "@/arches_vue_components/widgets/constants.ts";
import { buildFileListAliasedNodeData } from "@/arches_vue_components/datatypes/file-list/utils.ts";

import type {
    FileListAliasedNodeData,
    FileReference,
} from "@/arches_vue_components/datatypes/file-list/types.ts";
import type { FileListWidgetProps } from "@/arches_vue_components/widgets/FileListWidget/types.ts";

const {
    aliasedNodeData,
    value,
    metadataLanguageCode = undefined,
} = defineProps<FileListWidgetProps>();

const emit = defineEmits<{
    "update:value": [updatedValue: FileReference[] | null];
    "update:aliasedNodeData": [updatedValue: FileListAliasedNodeData];
    "update:metadataLanguageCode": [languageCode: string, fileIndex: number];
    initialized: [updatedValue: FileListAliasedNodeData];
    ready: [];
}>();

const resolvedAliasedNodeData = computed(
    () => aliasedNodeData ?? buildFileListAliasedNodeData(value ?? null),
);

onMounted(() => {
    emit("initialized", resolvedAliasedNodeData.value);
    emit("ready");
});

function onUpdateAliasedNodeData(
    updatedAliasedNodeData: FileListAliasedNodeData,
) {
    emit("update:aliasedNodeData", updatedAliasedNodeData);
    emit("update:value", updatedAliasedNodeData.node_value);
}
</script>

<template>
    <FileListWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="resolvedAliasedNodeData"
        :metadata-language-code="metadataLanguageCode"
        @update:aliased-node-data="onUpdateAliasedNodeData"
        @update:metadata-language-code="
            (languageCode, fileIndex) =>
                emit('update:metadataLanguageCode', languageCode, fileIndex)
        "
    />
    <FileListWidgetViewer
        v-if="mode === VIEW"
        :aliased-node-data="resolvedAliasedNodeData"
    />
</template>
