<script setup lang="ts">
import { ref, watchEffect } from "vue";

import Message from "primevue/message";
import Skeleton from "primevue/skeleton";

import DefaultCardEditor from "@/arches_component_lab/cards/DefaultCard/components/DefaultCardEditor.vue";
import DefaultCardViewer from "@/arches_component_lab/cards/DefaultCard/components/DefaultCardViewer.vue";

import {
    fetchCardData,
    fetchTileData,
} from "@/arches_component_lab/cards/api.ts";
import { fetchCardXNodeXWidgetDataFromNodeGroup } from "@/arches_component_lab/widgets/api.ts";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";

import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const props = defineProps<{
    mode: WidgetMode;
    nodegroupAlias: string;
    graphSlug: string;
    tileId?: string | null;
}>();

const emit = defineEmits(["update:isDirty", "update:tileData"]);

const isLoading = ref();
const configurationError = ref();

const cardData = ref();
const cardXNodeXWidgetData = ref<CardXNodeXWidget[]>([]);
const tileData = ref();

watchEffect(async () => {
    isLoading.value = true;

    try {
        const cardDataPromise = fetchCardData(
            props.graphSlug,
            props.nodegroupAlias,
        );
        const cardXNodeXWidgetDataPromise =
            fetchCardXNodeXWidgetDataFromNodeGroup(
                props.graphSlug,
                props.nodegroupAlias,
            );
        const tileDataPromise = fetchTileData(
            props.graphSlug,
            props.nodegroupAlias,
            props.tileId,
        );

        cardData.value = await cardDataPromise;
        cardXNodeXWidgetData.value = await cardXNodeXWidgetDataPromise;
        tileData.value = await tileDataPromise;
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
            <label>
                <span>{{ cardData.name }}</span>
            </label>

            <DefaultCardEditor
                v-if="props.mode === EDIT"
                v-model:tile-data="tileData"
                :card-x-node-x-widget-data="cardXNodeXWidgetData"
                :graph-slug="props.graphSlug"
                :mode="props.mode"
                :nodegroup-alias="props.nodegroupAlias"
                @update:is-dirty="emit('update:isDirty', $event)"
                @update:tile-data="emit('update:tileData', $event)"
            />
            <DefaultCardViewer
                v-else-if="props.mode === VIEW"
                v-model:tile-data="tileData"
                :card-x-node-x-widget-data="cardXNodeXWidgetData"
                :graph-slug="props.graphSlug"
                :mode="props.mode"
                :nodegroup-alias="props.nodegroupAlias"
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
