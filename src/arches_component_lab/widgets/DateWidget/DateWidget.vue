<script setup lang="ts">
import GenericWidget from "@/arches_component_lab/widgets/components/GenericWidget.vue";
import DateWidgetEditor from "@/arches_component_lab/widgets/DateWidget/components/DateWidgetEditor.vue";
import DateWidgetViewer from "@/arches_component_lab/widgets/DateWidget/components/DateWidgetViewer.vue";

import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

interface DateCardXNodeXWidgetData extends CardXNodeXWidget {
    config: {
        dateFormat: string;
        datePickerDisplayConfiguration: {
            dateFormat: string;
            shouldShowTime: boolean;
        };
    };
}

const props = withDefaults(
    defineProps<{
        mode: WidgetMode;
        nodeAlias: string;
        graphSlug: string;
        cardXNodeXWidgetData?: DateCardXNodeXWidgetData;
        value?: string | null | undefined;
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
            <DateWidgetEditor
                :card-x-node-x-widget-data="
                    slotProps.cardXNodeXWidgetData as DateCardXNodeXWidgetData
                "
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
            <DateWidgetViewer
                :card-x-node-x-widget-data="
                    slotProps.cardXNodeXWidgetData as DateCardXNodeXWidgetData
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
