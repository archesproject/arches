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

const { mode, nodegroupAlias, graphSlug, tileId } = defineProps<{
    mode: WidgetMode;
    nodegroupAlias: string;
    graphSlug: string;
    tileId?: string | null;
}>();

const emit = defineEmits(["update:isDirty", "update:tileData"]);

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
        }

        cardXNodeXWidgetData.value = await cardXNodeXWidgetDataPromise;
        console.log("!!!!", tileData.value, cardXNodeXWidgetData.value);
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
                @update:is-dirty="emit('update:isDirty', $event)"
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
