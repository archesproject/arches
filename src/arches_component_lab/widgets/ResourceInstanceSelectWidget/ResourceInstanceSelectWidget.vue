<script setup lang="ts">
import { computed, ref, toRef, watch } from "vue";

import ResourceInstanceSelectWidgetEditor from "@/arches_component_lab/widgets/ResourceInstanceSelectWidget/components/ResourceInstanceSelectWidgetEditor.vue";
import ResourceInstanceSelectWidgetViewer from "@/arches_component_lab/widgets/ResourceInstanceSelectWidget/components/ResourceInstanceSelectWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";
import { useResourceDisplayNameResolver } from "@/arches_component_lab/datatypes/resource-instance/useResourceDisplayNameResolver.ts";
import { buildResourceInstanceAliasedNodeData } from "@/arches_component_lab/datatypes/resource-instance/utils.ts";

import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";
import type {
    ResourceInstanceAliasedNodeData,
    ResourceInstanceReference,
} from "@/arches_component_lab/datatypes/resource-instance/types";

const {
    aliasedNodeData,
    mode,
    nodeAlias,
    graphSlug,
    cardXNodeXWidgetData,
    value,
    defaultTerm,
} = defineProps<{
    aliasedNodeData?: ResourceInstanceAliasedNodeData | null;
    mode: WidgetMode;
    nodeAlias?: string;
    graphSlug?: string;
    cardXNodeXWidgetData?: CardXNodeXWidgetData;
    value?: ResourceInstanceReference | null;
    defaultTerm?: string;
}>();

const emit = defineEmits<{
    "update:isLoading": [isLoading: boolean];
    "update:value": [updatedValue: ResourceInstanceReference | null];
    "update:aliasedNodeData": [updatedValue: ResourceInstanceAliasedNodeData];
    initialized: [updatedValue: ResourceInstanceAliasedNodeData];
}>();

const isEditorLoading = ref(false);

const { displayValue: resolvedDisplayValue, loading } =
    useResourceDisplayNameResolver(
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

    return buildResourceInstanceAliasedNodeData(
        value ?? null,
        resolvedDisplayValue.value ?? "",
    );
});

watch([loading, isEditorLoading], ([resolverLoading, editorLoading]) =>
    emit("update:isLoading", resolverLoading || editorLoading),
);

function onUpdateAliasedNodeData(
    updatedAliasedNodeData: ResourceInstanceAliasedNodeData,
) {
    emit("update:aliasedNodeData", updatedAliasedNodeData);
    emit("update:value", updatedAliasedNodeData.node_value?.[0] ?? null);
}
</script>

<template>
    <ResourceInstanceSelectWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :graph-slug="graphSlug"
        :node-alias="nodeAlias"
        :aliased-node-data="resolvedAliasedNodeData"
        :default-term="defaultTerm"
        @update:is-loading="isEditorLoading = $event"
        @update:aliased-node-data="onUpdateAliasedNodeData"
        @initialized="emit('initialized', $event)"
    />
    <ResourceInstanceSelectWidgetViewer
        v-if="mode === VIEW"
        :aliased-node-data="resolvedAliasedNodeData"
        @initialized="emit('initialized', $event)"
    />
</template>
