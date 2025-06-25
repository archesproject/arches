<script setup lang="ts">
import GenericWidget from "@/arches_component_lab/widgets/components/GenericWidget.vue";
import FileListWidgetViewer from "@/arches_component_lab/widgets/FileListWidget/components/FileListWidgetViewer.vue";
import FileListWidgetEditor from "@/arches_component_lab/widgets/FileListWidget/components/FileListWidgetEditor.vue";

import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";
import type {
    WidgetMode,
    FileReference,
} from "@/arches_component_lab/widgets/types.ts";

interface FileListCardXNodeXWidgetData extends CardXNodeXWidget {
    config: {
        acceptedFiles: string;
        maxFiles: number;
        maxFilesize: number;
        rerender: boolean;
        label: string;
    };
}

const props = withDefaults(
    defineProps<{
        mode: WidgetMode;
        nodeAlias: string;
        graphSlug: string;
        cardXNodeXWidgetData: FileListCardXNodeXWidgetData | undefined;
        value?: FileReference[] | null | undefined;
        showLabel?: boolean;
    }>(),
    {
        cardXNodeXWidgetData: undefined,
        showLabel: true,
        value: undefined,
    },
);

const emit = defineEmits(["update:isDirty", "update:value"]);
</script>

<template>
    <GenericWidget
        :graph-slug="props.graphSlug"
        :node-alias="props.nodeAlias"
        :mode="props.mode"
        :show-label="props.showLabel"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
    >
        <template #editor="slotProps">
            <FileListWidgetEditor
                :card-x-node-x-widget-data="
                    slotProps.cardXNodeXWidgetData as FileListCardXNodeXWidgetData
                "
                :graph-slug="props.graphSlug"
                :node-alias="props.nodeAlias"
                :value="props.value"
                @update:value="emit('update:value', $event)"
                @update:is-dirty="emit('update:isDirty', $event)"
            />
        </template>
        <template #viewer="slotProps">
            <FileListWidgetViewer
                :card-x-node-x-widget-data="
                    slotProps.cardXNodeXWidgetData as FileListCardXNodeXWidgetData
                "
                :value="props.value"
            />
        </template>
    </GenericWidget>
</template>

<style scoped>
.widget {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    width: 100%;
}
</style>
