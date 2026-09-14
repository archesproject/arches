<script setup lang="ts">
import { computed, ref, toRef, watch } from "vue";

import ConceptMultiSelectWidgetEditor from "@/arches_vue_components/widgets/ConceptMultiselectWidget/components/ConceptMultiselectWidgetEditor.vue";
import ConceptMultiSelectWidgetViewer from "@/arches_vue_components/widgets/ConceptMultiselectWidget/components/ConceptMultiselectWidgetViewer.vue";

import { useConceptLabelsResolver } from "@/arches_vue_components/datatypes/concept-list/useConceptLabelsResolver.ts";
import { buildConceptListAliasedNodeData } from "@/arches_vue_components/datatypes/concept-list/utils.ts";

import { EDIT, VIEW } from "@/arches_vue_components/widgets/constants.ts";

import type { ConceptListAliasedNodeData } from "@/arches_vue_components/datatypes/concept-list/types.ts";
import type { ConceptMultiselectWidgetProps } from "@/arches_vue_components/widgets/ConceptMultiselectWidget/types.ts";

const { aliasedNodeData, graphSlug, nodeAlias, value, mode } =
    defineProps<ConceptMultiselectWidgetProps>();

const emit = defineEmits<{
    "update:isLoading": [isLoading: boolean];
    "update:value": [updatedValue: string[] | null];
    "update:aliasedNodeData": [updatedValue: ConceptListAliasedNodeData];
    initialized: [updatedValue: ConceptListAliasedNodeData];
    ready: [];
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

if (resolvedAliasedNodeData.value) {
    emit("initialized", resolvedAliasedNodeData.value);
    if (mode === VIEW) {
        emit("ready");
    }
} else {
    watch(
        resolvedAliasedNodeData,
        (updatedAliasedNodeData) => {
            if (!updatedAliasedNodeData) {
                return;
            }
            emit("initialized", updatedAliasedNodeData);
            if (mode === VIEW) {
                emit("ready");
            }
        },
        { once: true },
    );
}

function onUpdateAliasedNodeData(
    updatedAliasedNodeData: ConceptListAliasedNodeData,
) {
    emit("update:aliasedNodeData", updatedAliasedNodeData);
    emit("update:value", updatedAliasedNodeData.node_value);
}
</script>

<template>
    <ConceptMultiSelectWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :graph-slug="graphSlug"
        :node-alias="nodeAlias"
        :aliased-node-data="resolvedAliasedNodeData"
        @update:is-loading="isEditorLoading = $event"
        @update:aliased-node-data="onUpdateAliasedNodeData"
        @ready="emit('ready')"
    />
    <ConceptMultiSelectWidgetViewer
        v-if="mode === VIEW"
        :aliased-node-data="resolvedAliasedNodeData"
    />
</template>
