<script setup lang="ts">
import NonLocalizedTextAreaWidgetEditor from "@/arches_component_lab/widgets/NonLocalizedTextAreaWidget/components/NonLocalizedTextAreaWidgetEditor.vue";
import NonLocalizedTextAreaWidgetViewer from "@/arches_component_lab/widgets/NonLocalizedTextAreaWidget/components/NonLocalizedTextAreaWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";

import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

defineProps<{
    mode: WidgetMode;
    nodeAlias: string;
    graphSlug: string;
    cardXNodeXWidgetData: CardXNodeXWidget;
    value: string | null | undefined;
}>();

const emit = defineEmits(["update:isDirty", "update:value"]);
</script>

<template>
    <NonLocalizedTextAreaWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :node-alias="nodeAlias"
        :value="value"
        @update:value="emit('update:value', $event)"
        @update:is-dirty="emit('update:isDirty', $event)"
    />
    <NonLocalizedTextAreaWidgetViewer
        v-if="mode === VIEW"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :value="value"
    />
</template>
