<script setup lang="ts">
import FileListWidgetViewer from "@/arches_component_lab/widgets/FileListWidget/components/FileListWidgetViewer.vue";
import FileListWidgetEditor from "@/arches_component_lab/widgets/FileListWidget/components/FileListWidgetEditor.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";

import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";
import type {
    WidgetMode,
    FileReference,
} from "@/arches_component_lab/widgets/types.ts";

interface FileListCardXNodeXWidgetData extends CardXNodeXWidget {
    config: CardXNodeXWidget["config"] & {
        acceptedFiles: string;
        maxFiles: number;
        maxFilesize: number;
        rerender: boolean;
        label: string;
    };
}

defineProps<{
    mode: WidgetMode;
    nodeAlias: string;
    graphSlug: string;
    cardXNodeXWidgetData: FileListCardXNodeXWidgetData | undefined;
    value: FileReference[] | null | undefined;
}>();

const emit = defineEmits(["update:isDirty", "update:value"]);
</script>

<template>
    <FileListWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="
            cardXNodeXWidgetData as FileListCardXNodeXWidgetData
        "
        :node-alias="nodeAlias"
        :value="value"
        @update:value="emit('update:value', $event)"
        @update:is-dirty="emit('update:isDirty', $event)"
    />
    <FileListWidgetViewer
        v-if="mode === VIEW"
        :card-x-node-x-widget-data="
            cardXNodeXWidgetData as FileListCardXNodeXWidgetData
        "
        :value="value"
    />
</template>
