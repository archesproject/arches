<script setup lang="ts">
import DateWidgetEditor from "@/arches_component_lab/widgets/DateWidget/components/DateWidgetEditor.vue";
import DateWidgetViewer from "@/arches_component_lab/widgets/DateWidget/components/DateWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";

import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

interface DateCardXNodeXWidgetData extends CardXNodeXWidget {
    config: CardXNodeXWidget["config"] & {
        dateFormat: string;
        datePickerDisplayConfiguration: {
            dateFormat: string;
            shouldShowTime: boolean;
        };
    };
}

defineProps<{
    mode: WidgetMode;
    nodeAlias: string;
    graphSlug: string;
    cardXNodeXWidgetData: DateCardXNodeXWidgetData;
    value: string | null | undefined;
}>();

const emit = defineEmits(["update:isDirty", "update:value"]);
</script>

<template>
    <DateWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="
            cardXNodeXWidgetData as DateCardXNodeXWidgetData
        "
        :node-alias="nodeAlias"
        :value="value"
        @update:value="emit('update:value', $event)"
        @update:is-dirty="emit('update:isDirty', $event)"
    />
    <DateWidgetViewer
        v-if="mode === VIEW"
        :card-x-node-x-widget-data="
            cardXNodeXWidgetData as DateCardXNodeXWidgetData
        "
        :value="value"
    />
</template>
