<script setup lang="ts">
import { ref, useTemplateRef, watchEffect } from "vue";

import Message from "primevue/message";
import Skeleton from "primevue/skeleton";

import GenericCardEditor from "@/arches_component_lab/generics/GenericCard/components/GenericCardEditor.vue";
import GenericCardViewer from "@/arches_component_lab/generics/GenericCard/components/GenericCardViewer.vue";

import { fetchTileData } from "@/arches_component_lab/generics/GenericCard/api.ts";
import { useNodegroupWidgetConfigStore } from "@/arches_component_lab/stores/useNodegroupWidgetConfigStore.ts";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";

import type {
    AliasedNodeData,
    AliasedTileData,
    CardXNodeXWidgetData,
} from "@/arches_component_lab/types.ts";
import type { GenericCardProps } from "@/arches_component_lab/generics/GenericCard/types.ts";

const {
    mode,
    nodegroupAlias,
    graphSlug,
    resourceInstanceId,
    selectedNodeAlias,
    shouldShowFormButtons = true,
    tileData,
    tileId,
} = defineProps<GenericCardProps>();

const emit = defineEmits<{
    "update:tileData": [tileData: AliasedTileData];
    "update:widgetDirtyStates": [widgetDirtyStates: Record<string, boolean>];
    "update:widgetFocusStates": [widgetFocusStates: Record<string, boolean>];
    save: [tileData: AliasedTileData];
    reset: [aliasedNodeDataMap: Record<string, AliasedNodeData>];
    initialized: [aliasedNodeData: Record<string, AliasedNodeData>];
}>();

const isLoading = ref(true);
const configurationError = ref();
const cardXNodeXWidgetData = ref<CardXNodeXWidgetData[]>([]);
const aliasedTileData = ref<AliasedTileData>();

const defaultCardEditor = useTemplateRef("defaultCardEditor");

watchEffect(async () => {
    isLoading.value = true;

    try {
        const cardXNodeXWidgetDataPromise =
            useNodegroupWidgetConfigStore().fetchNodegroupWidgetConfigs(
                graphSlug,
                nodegroupAlias,
            );

        if (tileData) {
            aliasedTileData.value = tileData;
        } else {
            aliasedTileData.value = await fetchTileData(
                graphSlug,
                nodegroupAlias,
                tileId,
            );
            if (!tileId && resourceInstanceId) {
                aliasedTileData.value.resourceinstance = resourceInstanceId;
            }
        }

        cardXNodeXWidgetData.value = await cardXNodeXWidgetDataPromise;
    } catch (error) {
        configurationError.value = error;
    } finally {
        isLoading.value = false;
    }
});

defineExpose({
    save: function () {
        if (defaultCardEditor.value) {
            defaultCardEditor.value.save();
        }
    },
});
</script>

<template>
    <div class="card">
        <Skeleton
            v-if="isLoading"
            style="height: 10rem"
        />
        <Message
            v-else-if="configurationError"
            severity="error"
        >
            {{ configurationError.message }}
        </Message>
        <template v-else>
            <span class="card-name">{{
                cardXNodeXWidgetData[0].card.name
            }}</span>

            <GenericCardEditor
                v-if="mode === EDIT"
                ref="defaultCardEditor"
                v-model:tile-data="aliasedTileData"
                :card-x-node-x-widget-data="cardXNodeXWidgetData"
                :graph-slug="graphSlug"
                :nodegroup-alias="nodegroupAlias"
                :resource-instance-id="resourceInstanceId"
                :selected-node-alias="selectedNodeAlias"
                :should-show-form-buttons="shouldShowFormButtons"
                @save="emit('save', $event)"
                @reset="emit('reset', $event)"
                @update:tile-data="emit('update:tileData', $event)"
                @update:widget-dirty-states="
                    emit('update:widgetDirtyStates', $event)
                "
                @update:widget-focus-states="
                    emit('update:widgetFocusStates', $event)
                "
                @initialized="emit('initialized', $event)"
            />
            <GenericCardViewer
                v-else-if="mode === VIEW"
                v-model:tile-data="aliasedTileData"
                :card-x-node-x-widget-data="cardXNodeXWidgetData"
                :graph-slug="graphSlug"
                :nodegroup-alias="nodegroupAlias"
                @initialized="emit('initialized', $event)"
            />
        </template>
    </div>
</template>

<style scoped>
.card {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    width: 100%;
}
.card-name {
    font-size: 1.8rem;
    font-weight: 600;
    margin-bottom: 1rem;
}
</style>
