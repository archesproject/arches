<script setup lang="ts">
import NonLocalizedTextWidgetEditor from "@/arches_component_lab/widgets/NonLocalizedTextWidget/components/NonLocalizedTextWidgetEditor.vue";
import NonLocalizedTextWidgetViewer from "@/arches_component_lab/widgets/NonLocalizedTextWidget/components/NonLocalizedTextWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";

import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { NonLocalizedTextValue } from "@/arches_component_lab/datatypes/non-localized-text/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

defineProps<{
    mode: WidgetMode;
    nodeAlias: string;
    graphSlug: string;
    cardXNodeXWidgetData: CardXNodeXWidgetData;
    value: NonLocalizedTextValue;
}>();

const emit = defineEmits(["update:isDirty", "update:value"]);
</script>

<template>
    <NonLocalizedTextWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :graph-slug="graphSlug"
        :node-alias="nodeAlias"
        :value="value"
        @update:value="emit('update:value', $event)"
        @update:is-dirty="emit('update:isDirty', $event)"
    />
    <NonLocalizedTextWidgetViewer
        v-if="mode === VIEW"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :value="value"
    />
</template>
