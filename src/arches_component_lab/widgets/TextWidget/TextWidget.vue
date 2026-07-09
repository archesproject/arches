<script setup lang="ts">
import { computed } from "vue";

import { useGettext } from "vue3-gettext";

import TextWidgetEditor from "@/arches_component_lab/widgets/TextWidget/components/TextWidgetEditor.vue";
import TextWidgetViewer from "@/arches_component_lab/widgets/TextWidget/components/TextWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";
import { buildStringAliasedNodeData } from "@/arches_component_lab/datatypes/string/utils.ts";

import type { StringCardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type {
    LanguageValue,
    StringAliasedNodeData,
} from "@/arches_component_lab/datatypes/string/types";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const { aliasedNodeData, value } = defineProps<{
    mode: WidgetMode;
    nodeAlias?: string;
    graphSlug?: string;
    cardXNodeXWidgetData?: StringCardXNodeXWidgetData;
    aliasedNodeData?: StringAliasedNodeData | null;
    value?: Record<string, LanguageValue> | null;
    renderContext?: string;
}>();

const emit = defineEmits<{
    "update:value": [updatedValue: Record<string, LanguageValue> | null];
    "update:aliasedNodeData": [updatedValue: StringAliasedNodeData];
    initialized: [updatedValue: StringAliasedNodeData];
}>();

const { current } = useGettext();
const resolvedAliasedNodeData = computed(
    () => aliasedNodeData ?? buildStringAliasedNodeData(value ?? null, current),
);

function onUpdateAliasedNodeData(
    updatedAliasedNodeData: StringAliasedNodeData,
) {
    emit("update:aliasedNodeData", updatedAliasedNodeData);
    emit("update:value", updatedAliasedNodeData.node_value);
}
</script>

<template>
    <TextWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="resolvedAliasedNodeData"
        :render-context="renderContext"
        @update:aliased-node-data="onUpdateAliasedNodeData"
        @initialized="emit('initialized', $event)"
    />
    <TextWidgetViewer
        v-if="mode === VIEW"
        :aliased-node-data="resolvedAliasedNodeData"
        @initialized="emit('initialized', $event)"
    />
</template>
