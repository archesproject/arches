<script setup lang="ts">
import { ref, useTemplateRef, watchEffect } from "vue";

import Message from "primevue/message";
import Skeleton from "primevue/skeleton";

import GenericCardEditor from "@/arches_component_lab/generics/GenericCard/components/GenericCardEditor.vue";
import GenericCardViewer from "@/arches_component_lab/generics/GenericCard/components/GenericCardViewer.vue";

import {
    fetchTileData,
    fetchCardXNodeXWidgetDataFromNodeGroup,
} from "@/arches_component_lab/generics/GenericCard/api.ts";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";

import type {
    AliasedTileData,
    CardXNodeXWidgetData,
} from "@/arches_component_lab/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const {
    mode,
    nodegroupAlias,
    graphSlug,
    resourceInstanceId,
    selectedNodeAlias,
    shouldShowFormButtons = true,
    tileData,
    tileId,
} = defineProps<{
    mode: WidgetMode;
    nodegroupAlias: string;
    graphSlug: string;
    resourceInstanceId?: string | null;
    selectedNodeAlias?: string | null;
    shouldShowFormButtons?: boolean;
    tileData?: AliasedTileData;
    tileId?: string | null;
}>();

const emit = defineEmits([
    "update:tileData",
    "update:widgetDirtyStates",
    "update:widgetFocusStates",
    "save",
    "reset",
]);

const isLoading = ref(true);
const configurationError = ref();
const cardXNodeXWidgetData = ref<CardXNodeXWidgetData[]>([]);
const aliasedTileData = ref<AliasedTileData>();

const defaultCardEditor = useTemplateRef("defaultCardEditor");

watchEffect(async () => {
    isLoading.value = true;

    try {
        if (!tileData && !tileId && !resourceInstanceId) {
            throw new Error();
        }

        const cardXNodeXWidgetDataPromise =
            fetchCardXNodeXWidgetDataFromNodeGroup(graphSlug, nodegroupAlias);

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
            <span>{{ cardXNodeXWidgetData[0].card.name }}</span>

            <GenericCardEditor
                v-if="mode === EDIT"
                ref="defaultCardEditor"
                v-model:tile-data="aliasedTileData"
                :card-x-node-x-widget-data="cardXNodeXWidgetData"
                :graph-slug="graphSlug"
                :mode="mode"
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
            />
            <GenericCardViewer
                v-else-if="mode === VIEW"
                v-model:tile-data="aliasedTileData"
                :card-x-node-x-widget-data="cardXNodeXWidgetData"
                :graph-slug="graphSlug"
                :mode="mode"
                :nodegroup-alias="nodegroupAlias"
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
</style>
