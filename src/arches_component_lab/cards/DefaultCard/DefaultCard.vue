<script setup lang="ts">
import { ref, watchEffect } from "vue";

import Message from "primevue/message";
import Skeleton from "primevue/skeleton";

import DefaultCardEditor from "@/arches_component_lab/cards/DefaultCard/components/DefaultCardEditor.vue";
import DefaultCardViewer from "@/arches_component_lab/cards/DefaultCard/components/DefaultCardViewer.vue";

import { fetchTileData } from "@/arches_component_lab/cards/api.ts";
import { fetchCardXNodeXWidgetDataFromNodeGroup } from "@/arches_component_lab/cards/api.ts";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";

import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";
import type { AliasedTileData } from "@/arches_component_lab/cards/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const { mode, nodegroupAlias, graphSlug, resourceInstanceId, tileId } =
    defineProps<{
        mode: WidgetMode;
        nodegroupAlias: string;
        graphSlug: string;
        resourceInstanceId?: string | null;
        tileId?: string | null;
    }>();

const emit = defineEmits(["update:widgetDirtyStates", "update:tileData"]);

const isLoading = ref(false);
const configurationError = ref();

const cardXNodeXWidgetData = ref<CardXNodeXWidget[]>([]);
const tileData = ref<AliasedTileData>();

watchEffect(async () => {
    isLoading.value = true;

    try {
        const cardXNodeXWidgetDataPromise =
            fetchCardXNodeXWidgetDataFromNodeGroup(graphSlug, nodegroupAlias);

        if (tileId) {
            const tileDataPromise = fetchTileData(
                graphSlug,
                nodegroupAlias,
                tileId,
            );
            tileData.value = await tileDataPromise;
        } else if (resourceInstanceId) {
            // TODO: Replace with querysets call for empty tile structure
            // @ts-expect-error this is an incomplete tile structure
            tileData.value = {
                resourceinstance: resourceInstanceId,
                aliased_data: {},
            };
        }

        cardXNodeXWidgetData.value = await cardXNodeXWidgetDataPromise;
    } catch (error) {
        configurationError.value = error;
    } finally {
        isLoading.value = false;
    }
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

            <DefaultCardEditor
                v-if="mode === EDIT"
                v-model:tile-data="tileData"
                :card-x-node-x-widget-data="cardXNodeXWidgetData"
                :graph-slug="graphSlug"
                :mode="mode"
                :nodegroup-alias="nodegroupAlias"
                :resource-instance-id="resourceInstanceId"
                @update:widget-dirty-states="
                    emit('update:widgetDirtyStates', $event)
                "
                @update:tile-data="emit('update:tileData', $event)"
            />
            <DefaultCardViewer
                v-else-if="mode === VIEW"
                v-model:tile-data="tileData"
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
