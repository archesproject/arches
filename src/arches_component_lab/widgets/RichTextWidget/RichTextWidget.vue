<script setup lang="ts">
import { computed } from "vue";

import { useGettext } from "vue3-gettext";

import RichTextWidgetEditor from "@/arches_component_lab/widgets/RichTextWidget/components/RichTextWidgetEditor/RichTextWidgetEditor.vue";
import RichTextWidgetViewer from "@/arches_component_lab/widgets/RichTextWidget/components/RichTextWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";
import { buildStringAliasedNodeData } from "@/arches_component_lab/datatypes/string/utils.ts";

import type {
    LanguageValue,
    StringAliasedNodeData,
} from "@/arches_component_lab/datatypes/string/types.ts";
import type { RichTextWidgetProps } from "@/arches_component_lab/widgets/RichTextWidget/types.ts";

const { aliasedNodeData, value } = defineProps<RichTextWidgetProps>();

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
    <RichTextWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="resolvedAliasedNodeData"
        @update:aliased-node-data="onUpdateAliasedNodeData"
        @initialized="emit('initialized', $event)"
    />
    <RichTextWidgetViewer
        v-if="mode === VIEW"
        :aliased-node-data="resolvedAliasedNodeData"
        @initialized="emit('initialized', $event)"
    />
</template>
