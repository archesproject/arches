<script setup lang="ts">
import { computed, ref, useTemplateRef, watch, watchEffect } from "vue";

import Message from "openvue/message";
import Skeleton from "openvue/skeleton";

import GenericCardEditor from "@/arches_vue_components/generics/GenericCard/components/GenericCardEditor.vue";
import GenericCardViewer from "@/arches_vue_components/generics/GenericCard/components/GenericCardViewer.vue";

import { fetchTileData } from "@/arches_vue_components/generics/GenericCard/api.ts";
import { useLanguageStore } from "@/arches_vue_components/stores/useLanguageStore.ts";
import { useNodegroupWidgetConfigStore } from "@/arches_vue_components/stores/useNodegroupWidgetConfigStore.ts";

import { EDIT, VIEW } from "@/arches_vue_components/widgets/constants.ts";

import type {
    AliasedNodeData,
    AliasedTileData,
    CardXNodeXWidgetData,
} from "@/arches_vue_components/types.ts";
import type { GenericCardProps } from "@/arches_vue_components/generics/GenericCard/types.ts";

const {
    mode,
    nodegroupAlias,
    graphSlug,
    resourceInstanceId,
    selectedNodeAlias,
    shouldShowCardName = true,
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

const languageStore = useLanguageStore();
const nodegroupWidgetConfigStore = useNodegroupWidgetConfigStore();

const isLoading = ref(true);
const configurationError = ref();
const cardXNodeXWidgetData = ref<CardXNodeXWidgetData[]>([]);
const aliasedTileData = ref<AliasedTileData>();

const defaultCardEditor = useTemplateRef("defaultCardEditor");

const shouldFetchTile = computed(() => tileData === undefined);

watch(
    () => tileData,
    (newTileData) => {
        if (newTileData !== undefined) {
            aliasedTileData.value = newTileData;
        }
    },
    { immediate: true },
);

watchEffect(async (onCleanup) => {
    let isStale = false;
    onCleanup(() => {
        isStale = true;
    });
    isLoading.value = true;

    let tileDataPromise: Promise<AliasedTileData | undefined> =
        Promise.resolve(undefined);
    if (shouldFetchTile.value) {
        tileDataPromise = fetchTileData(graphSlug, nodegroupAlias, tileId);
    }
    let languagesPromise: Promise<unknown> = Promise.resolve();
    if (mode === EDIT) {
        languagesPromise = languageStore
            .fetchAllLanguages()
            .catch(() => undefined);
    }

    try {
        const [loadedCardXNodeXWidgetData, loadedTileData] = await Promise.all([
            nodegroupWidgetConfigStore.fetchNodegroupWidgetConfigs(
                graphSlug,
                nodegroupAlias,
            ),
            tileDataPromise,
            languagesPromise,
        ]);
        if (isStale) {
            return;
        }
        if (loadedTileData) {
            aliasedTileData.value = loadedTileData;
            if (!tileId && resourceInstanceId) {
                aliasedTileData.value.resourceinstance = resourceInstanceId;
            }
        }
        cardXNodeXWidgetData.value = loadedCardXNodeXWidgetData;
    } catch (error) {
        if (!isStale) {
            configurationError.value = error;
        }
    } finally {
        if (!isStale) {
            isLoading.value = false;
        }
    }
});

defineExpose({
    save: function () {
        if (defaultCardEditor.value) {
            defaultCardEditor.value.save();
        }
    },
    focusWidgetInputForNodeAlias: async function (
        nodeAlias: string,
    ): Promise<void> {
        if (defaultCardEditor.value) {
            await defaultCardEditor.value.focusWidgetInputForNodeAlias(
                nodeAlias,
            );
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
            <span
                v-if="shouldShowCardName"
                class="card-name"
            >
                {{ cardXNodeXWidgetData[0].card.name }}
            </span>

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
