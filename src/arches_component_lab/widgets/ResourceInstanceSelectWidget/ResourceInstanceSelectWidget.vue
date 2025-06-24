<script setup lang="ts">
import GenericWidget from "@/arches_component_lab/widgets/components/GenericWidget.vue";
import ResourceInstanceSelectWidgetEditor from "@/arches_component_lab/widgets/ResourceInstanceSelectWidget/components/ResourceInstanceSelectWidgetEditor.vue";
import ResourceInstanceSelectWidgetViewer from "@/arches_component_lab/widgets/ResourceInstanceSelectWidget/components/ResourceInstanceSelectWidgetViewer.vue";

import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";
import type {
    ResourceInstanceReference,
    WidgetMode,
} from "@/arches_component_lab/widgets/types.ts";

const props = withDefaults(
    defineProps<{
        mode: WidgetMode;
        nodeAlias: string;
        graphSlug: string;
        cardXNodeXWidgetData?: CardXNodeXWidget;
        value?: ResourceInstanceReference | null | undefined;
        showLabel?: boolean;
    }>(),
    {
        cardXNodeXWidgetData: undefined,
        initialValue: undefined,
        showLabel: true,
        value: undefined,
    },
);

const emit = defineEmits(["update:value"]);
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
            <ResourceInstanceSelectWidgetEditor
                :card-x-node-x-widget-data="slotProps.cardXNodeXWidgetData"
                :graph-slug="graphSlug"
                :node-alias="nodeAlias"
                :value="props.value"
                @update:value="
                    (value) => {
                        emit('update:value', value);
                    }
                "
            />
        </template>
        <template #viewer="slotProps">
            <ResourceInstanceSelectWidgetViewer
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
