<script setup lang="ts">
import GenericWidget from "@/arches_component_lab/widgets/components/GenericWidget.vue";
import NonLocalizedStringWidgetEditor from "@/arches_component_lab/widgets/NonLocalizedStringWidget/components/NonLocalizedStringWidgetEditor.vue";
import NonLocalizedStringWidgetViewer from "@/arches_component_lab/widgets/NonLocalizedStringWidget/components/NonLocalizedStringWidgetViewer.vue";

import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const props = withDefaults(
    defineProps<{
        mode: WidgetMode;
        nodeAlias: string;
        graphSlug: string;
        cardXNodeXWidgetData?: CardXNodeXWidget;
        value?: string | null;
        showLabel?: boolean;
    }>(),
    {
        cardXNodeXWidgetData: undefined,
        initialValue: undefined,
        showLabel: true,
    },
);
</script>

<template>
    <GenericWidget
        :graph-slug="props.graphSlug"
        :node-alias="props.nodeAlias"
        :mode="props.mode"
        :show-label="props.showLabel"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :editor-component="NonLocalizedStringWidgetEditor"
        :viewer-component="NonLocalizedStringWidgetViewer"
    >
        <template #editor="{ cardXNodeXWidgetData }">
            <NonLocalizedStringWidgetEditor
                :card-x-node-x-widget-data="cardXNodeXWidgetData"
                :graph-slug="graphSlug"
                :node-alias="nodeAlias"
                :value="props.value"
            />
        </template>
        <template #viewer>
            <NonLocalizedStringWidgetViewer :value="props.value" />
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
