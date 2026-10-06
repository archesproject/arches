<script setup lang="ts">
import { computed, onMounted } from "vue";

import { useGettext } from "vue3-gettext";

import RichTextWidgetEditor from "@/arches_vue_components/widgets/RichTextWidget/components/RichTextWidgetEditor/RichTextWidgetEditor.vue";
import RichTextWidgetViewer from "@/arches_vue_components/widgets/RichTextWidget/components/RichTextWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_vue_components/widgets/constants.ts";
import { buildStringAliasedNodeData } from "@/arches_vue_components/datatypes/string/utils.ts";

import type {
    LanguageValue,
    StringAliasedNodeData,
} from "@/arches_vue_components/datatypes/string/types.ts";
import type { RichTextWidgetProps } from "@/arches_vue_components/widgets/RichTextWidget/types.ts";

const { aliasedNodeData, value, mode } = defineProps<RichTextWidgetProps>();

const emit = defineEmits<{
    "update:value": [updatedValue: Record<string, LanguageValue> | null];
    "update:aliasedNodeData": [updatedValue: StringAliasedNodeData];
    initialized: [updatedValue: StringAliasedNodeData];
    ready: [];
}>();

const { current } = useGettext();
const resolvedAliasedNodeData = computed(
    () => aliasedNodeData ?? buildStringAliasedNodeData(value ?? null, current),
);

onMounted(() => {
    emit("initialized", resolvedAliasedNodeData.value);
    if (mode === VIEW) {
        emit("ready");
    }
});

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
        @ready="emit('ready')"
    />
    <RichTextWidgetViewer
        v-if="mode === VIEW"
        :aliased-node-data="resolvedAliasedNodeData"
    />
</template>
