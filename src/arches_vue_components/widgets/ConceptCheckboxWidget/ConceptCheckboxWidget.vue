<script setup lang="ts">
import { computed, ref, toRef, watch } from "vue";

import ConceptCheckboxWidgetEditor from "@/arches_vue_components/widgets/ConceptCheckboxWidget/components/ConceptCheckboxWidgetEditor.vue";
import ConceptCheckboxWidgetViewer from "@/arches_vue_components/widgets/ConceptCheckboxWidget/components/ConceptCheckboxWidgetViewer.vue";

import { useConceptLabelsResolver } from "@/arches_vue_components/datatypes/concept-list/useConceptLabelsResolver.ts";
import { buildConceptListAliasedNodeData } from "@/arches_vue_components/datatypes/concept-list/utils.ts";

import { EDIT, VIEW } from "@/arches_vue_components/widgets/constants.ts";

import type { ConceptListAliasedNodeData } from "@/arches_vue_components/datatypes/concept-list/types.ts";
import type { ConceptCheckboxWidgetProps } from "@/arches_vue_components/widgets/ConceptCheckboxWidget/types.ts";

const { aliasedNodeData, graphSlug, nodeAlias, value } =
    defineProps<ConceptCheckboxWidgetProps>();

const emit = defineEmits<{
    "update:isLoading": [isLoading: boolean];
    "update:value": [updatedValue: string[] | null];
    "update:aliasedNodeData": [updatedValue: ConceptListAliasedNodeData];
    initialized: [updatedValue: ConceptListAliasedNodeData];
}>();

const { resolvedItems, loading } = useConceptLabelsResolver(
    toRef(() => {
        if (!aliasedNodeData) {
            return value ?? null;
        }
        return null;
    }),
    graphSlug ?? "",
    nodeAlias ?? "",
);

const isEditorLoading = ref(false);

const resolvedAliasedNodeData = computed(() => {
    if (aliasedNodeData) {
        return aliasedNodeData;
    }
    if (loading.value) {
        return null;
    }

    return buildConceptListAliasedNodeData(value ?? null, resolvedItems.value);
});

watch([loading, isEditorLoading], ([resolverLoading, editorLoading]) =>
    emit("update:isLoading", resolverLoading || editorLoading),
);

function onUpdateAliasedNodeData(
    updatedAliasedNodeData: ConceptListAliasedNodeData,
) {
    emit("update:aliasedNodeData", updatedAliasedNodeData);
    emit("update:value", updatedAliasedNodeData.node_value);
}
</script>

<template>
    <ConceptCheckboxWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :graph-slug="graphSlug"
        :node-alias="nodeAlias"
        :aliased-node-data="resolvedAliasedNodeData"
        @update:is-loading="isEditorLoading = $event"
        @update:aliased-node-data="onUpdateAliasedNodeData"
        @initialized="emit('initialized', $event)"
    />
    <ConceptCheckboxWidgetViewer
        v-if="mode === VIEW"
        :aliased-node-data="resolvedAliasedNodeData"
        @initialized="emit('initialized', $event)"
    />
</template>
