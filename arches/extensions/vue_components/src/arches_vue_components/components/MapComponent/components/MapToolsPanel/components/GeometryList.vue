<script setup lang="ts">
import { nextTick, useTemplateRef, watch } from "vue";

import { useGettext } from "vue3-gettext";

import Button from "openvue/button";

import GeometryRow from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/GeometryRow.vue";

import { useDrawnFeatureLabels } from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/composables/useDrawnFeatureLabels.ts";
import { useResolvedMapContext } from "@/arches_vue_components/components/MapComponent/composables/useMapContext.ts";

import type { MapContext } from "@/arches_vue_components/components/MapComponent/types.ts";

const EDIT_COORDINATES_EVENT = "edit-coordinates" as const;

const { context = undefined } = defineProps<{
    context?: MapContext;
}>();

const emit = defineEmits<{
    (event: typeof EDIT_COORDINATES_EVENT, featureId: string): void;
}>();

const listElement = useTemplateRef<HTMLDivElement>("listElement");

const resolvedContext = useResolvedMapContext(context, "GeometryList");
const { drawnFeatures, selectedDrawnFeature, deleteAllDrawnFeatures } =
    resolvedContext;
const labelsByFeatureId = useDrawnFeatureLabels(drawnFeatures);

const { $gettext } = useGettext();

watch(
    () => selectedDrawnFeature.value?.id,
    async (selectedFeatureId) => {
        if (selectedFeatureId === undefined) {
            return;
        }

        await nextTick();
        listElement.value
            ?.querySelector(`[data-feature-id="${selectedFeatureId}"]`)
            ?.scrollIntoView({ block: "nearest" });
    },
);
</script>

<template>
    <div class="geometry-list">
        <div class="geometry-list-header">
            <span class="geometry-list-title">{{
                $gettext("Geometries")
            }}</span>
            <Button
                size="small"
                :label="$gettext('Remove all')"
                :link="true"
                @click="deleteAllDrawnFeatures"
            />
        </div>
        <div
            ref="listElement"
            class="geometry-list-rows"
        >
            <GeometryRow
                v-for="feature in drawnFeatures"
                :key="String(feature.id)"
                :data-feature-id="String(feature.id)"
                :feature="feature"
                :label="labelsByFeatureId[String(feature.id)]"
                :is-selected="selectedDrawnFeature?.id === feature.id"
                :context="resolvedContext"
                @edit-coordinates="emit(EDIT_COORDINATES_EVENT, $event)"
            />
        </div>
    </div>
</template>

<style scoped>
.geometry-list {
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
}

.geometry-list-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.8rem;
}

.geometry-list-title {
    color: var(--p-text-muted-color);
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 0.06rem;
    text-transform: uppercase;
}

.geometry-list-rows {
    display: flex;
    flex-direction: column;
}
</style>
