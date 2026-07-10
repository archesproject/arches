<script setup lang="ts">
import { computed } from "vue";

import FileListWidgetViewer from "@/arches_component_lab/widgets/FileListWidget/components/FileListWidgetViewer.vue";
import FileListWidgetEditor from "@/arches_component_lab/widgets/FileListWidget/components/FileListWidgetEditor/FileListWidgetEditor.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";
import { buildFileListAliasedNodeData } from "@/arches_component_lab/datatypes/file-list/utils.ts";

import type {
    FileListAliasedNodeData,
    FileReference,
} from "@/arches_component_lab/datatypes/file-list/types.ts";
import type { FileListWidgetProps } from "@/arches_component_lab/widgets/FileListWidget/types.ts";

const { aliasedNodeData, value } = defineProps<FileListWidgetProps>();

const emit = defineEmits<{
    "update:value": [updatedValue: FileReference[] | null];
    "update:aliasedNodeData": [updatedValue: FileListAliasedNodeData];
    initialized: [updatedValue: FileListAliasedNodeData];
}>();

const resolvedAliasedNodeData = computed(
    () => aliasedNodeData ?? buildFileListAliasedNodeData(value ?? null),
);

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
        @update:aliased-node-data="onUpdateAliasedNodeData"
        @initialized="emit('initialized', $event)"
    />
    <FileListWidgetViewer
        v-if="mode === VIEW"
        :aliased-node-data="resolvedAliasedNodeData"
        @initialized="emit('initialized', $event)"
    />
</template>
