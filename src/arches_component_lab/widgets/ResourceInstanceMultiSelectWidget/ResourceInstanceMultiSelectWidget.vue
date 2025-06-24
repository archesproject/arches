<script setup lang="ts">
import GenericWidget from "@/arches_component_lab/widgets/components/GenericWidget.vue";
import ResourceInstanceMultiSelectWidgetEditor from "@/arches_component_lab/widgets/ResourceInstanceMultiSelectWidget/components/ResourceInstanceMultiSelectWidgetEditor.vue";
import ResourceInstanceMultiSelectWidgetViewer from "@/arches_component_lab/widgets/ResourceInstanceMultiSelectWidget/components/ResourceInstanceMultiSelectWidgetViewer.vue";

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
        value?: ResourceInstanceReference[] | null | undefined;
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
            <ResourceInstanceMultiSelectWidgetEditor
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
            <ResourceInstanceMultiSelectWidgetViewer
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
