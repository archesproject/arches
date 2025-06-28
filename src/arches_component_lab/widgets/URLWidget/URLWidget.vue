<script setup lang="ts">
import GenericWidget from "@/arches_component_lab/widgets/components/GenericWidget.vue";
import URLWidgetEditor from "@/arches_component_lab/widgets/URLWidget/components/URLWidgetEditor.vue";
import URLWidgetViewer from "@/arches_component_lab/widgets/URLWidget/components/URLWidgetViewer.vue";

import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";
import type {
    URLDatatype,
    WidgetMode,
} from "@/arches_component_lab/widgets/types.ts";

const props = withDefaults(
    defineProps<{
        mode: WidgetMode;
        nodeAlias: string;
        graphSlug: string;
        cardXNodeXWidgetData?: CardXNodeXWidget;
        value?: URLDatatype | null | undefined;
        showLabel?: boolean;
    }>(),
    {
        cardXNodeXWidgetData: undefined,
        initialValue: undefined,
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
            <URLWidgetEditor
                :card-x-node-x-widget-data="slotProps.cardXNodeXWidgetData"
                :graph-slug="graphSlug"
                :node-alias="nodeAlias"
                :value="props.value"
                @update:value="emit('update:value', $event)"
                @update:is-dirty="emit('update:isDirty', $event)"
            />
        </template>
        <template #viewer="slotProps">
            <URLWidgetViewer
                :card-x-node-x-widget-data="slotProps.cardXNodeXWidgetData"
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
