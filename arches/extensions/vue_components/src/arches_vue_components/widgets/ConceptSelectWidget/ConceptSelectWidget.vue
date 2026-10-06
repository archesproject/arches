<script setup lang="ts">
import { computed, ref, toRef, watch } from "vue";

import ConceptSelectWidgetEditor from "@/arches_vue_components/widgets/ConceptSelectWidget/components/ConceptSelectWidgetEditor.vue";
import ConceptSelectWidgetViewer from "@/arches_vue_components/widgets/ConceptSelectWidget/components/ConceptSelectWidgetViewer.vue";

import { useConceptLabelResolver } from "@/arches_vue_components/datatypes/concept/useConceptLabelResolver.ts";
import { buildConceptAliasedNodeData } from "@/arches_vue_components/datatypes/concept/utils.ts";

import { EDIT, VIEW } from "@/arches_vue_components/widgets/constants.ts";

import type { ConceptAliasedNodeData } from "@/arches_vue_components/datatypes/concept/types.ts";
import type { ConceptSelectWidgetProps } from "@/arches_vue_components/widgets/ConceptSelectWidget/types.ts";

const { aliasedNodeData, graphSlug, nodeAlias, value, mode } =
    defineProps<ConceptSelectWidgetProps>();

const emit = defineEmits<{
    "update:isLoading": [isLoading: boolean];
    "update:value": [updatedValue: string | null];
    "update:aliasedNodeData": [updatedValue: ConceptAliasedNodeData];
    initialized: [updatedValue: ConceptAliasedNodeData];
    ready: [];
}>();

const isEditorLoading = ref(false);

const { resolved, loading } = useConceptLabelResolver(
    toRef(() => {
        if (!aliasedNodeData) {
            return value ?? null;
        }
        return null;
    }),
    graphSlug ?? "",
    nodeAlias ?? "",
);

const resolvedAliasedNodeData = computed(() => {
    if (aliasedNodeData) {
        return aliasedNodeData;
    }
    if (loading.value) {
        return null;
    }

    return buildConceptAliasedNodeData(
        value ?? null,
        resolved.value ? [resolved.value] : [],
    );
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
    updatedAliasedNodeData: ConceptAliasedNodeData,
) {
    emit("update:aliasedNodeData", updatedAliasedNodeData);
    emit("update:value", updatedAliasedNodeData.node_value);
}
</script>

<template>
    <ConceptSelectWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :graph-slug="graphSlug"
        :node-alias="nodeAlias"
        :aliased-node-data="resolvedAliasedNodeData"
        @update:is-loading="isEditorLoading = $event"
        @update:aliased-node-data="onUpdateAliasedNodeData"
        @ready="emit('ready')"
    />
    <ConceptSelectWidgetViewer
        v-if="mode === VIEW"
        :aliased-node-data="resolvedAliasedNodeData"
    />
</template>
