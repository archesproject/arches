<script setup lang="ts">
import TextWidgetEditor from "@/arches_component_lab/widgets/TextWidget/components/TextWidgetEditor.vue";
import TextWidgetViewer from "@/arches_component_lab/widgets/TextWidget/components/TextWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";

import type { StringCardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { StringValue } from "@/arches_component_lab/datatypes/string/types";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

defineProps<{
    mode: WidgetMode;
    nodeAlias: string;
    graphSlug: string;
    cardXNodeXWidgetData: StringCardXNodeXWidgetData;
    aliasedNodeData: StringValue;
}>();

const emit = defineEmits(["update:value"]);
</script>

<template>
    <TextWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="aliasedNodeData"
        @update:value="emit('update:value', $event)"
    />
    <TextWidgetViewer
        v-if="mode === VIEW"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="aliasedNodeData"
    />
</template>
