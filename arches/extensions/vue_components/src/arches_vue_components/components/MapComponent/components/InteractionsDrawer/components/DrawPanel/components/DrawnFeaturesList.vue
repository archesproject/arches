<script setup lang="ts">
import { computed } from "vue";

import { useGettext } from "vue3-gettext";

import Listbox from "primevue/listbox";

import {
    GEOMETRY_TYPE_LINESTRING,
    GEOMETRY_TYPE_POINT,
    GEOMETRY_TYPE_POLYGON,
} from "@/arches_vue_components/components/MapComponent/constants.ts";
import { useResolvedMapContext } from "@/arches_vue_components/components/MapComponent/composables/useMapContext.ts";

import type { MapContext } from "@/arches_vue_components/components/MapComponent/types.ts";

const { context = undefined } = defineProps<{
    context?: MapContext;
}>();

const { drawnFeatures, selectedDrawnFeature, selectDrawnFeature } =
    useResolvedMapContext(context, "DrawnFeaturesList");

const { $gettext } = useGettext();

const labeledFeatures = computed(() => {
    const countByType: Record<string, number> = {};

    return drawnFeatures.value.map((feature) => {
        const type = feature.geometry.type;

        countByType[type] = (countByType[type] || 0) + 1;

        const count = String(countByType[type]);

        if (type === GEOMETRY_TYPE_POINT) {
            return {
                featureId: String(feature.id),
                feature,
                label: $gettext("Marker %{count}", { count }),
            };
        } else if (type === GEOMETRY_TYPE_LINESTRING) {
            return {
                featureId: String(feature.id),
                feature,
                label: $gettext("Polyline %{count}", { count }),
            };
        } else if (type === GEOMETRY_TYPE_POLYGON) {
            return {
                featureId: String(feature.id),
                feature,
                label: $gettext("Polygon %{count}", { count }),
            };
        } else {
            return {
                featureId: String(feature.id),
                feature,
                label: $gettext("Feature %{count}", { count }),
            };
        }
    });
});

const selectedFeatureId = computed(() =>
    selectedDrawnFeature.value ? String(selectedDrawnFeature.value.id) : null,
);

function onSelect(featureId: string): void {
    const item = labeledFeatures.value.find(
        (item) => item.featureId === featureId,
    );
    if (!item) return;
    selectDrawnFeature(item.feature);
}
</script>

<template>
    <Listbox
        v-if="drawnFeatures.length"
        class="drawn-features-list"
        option-label="label"
        option-value="featureId"
        :model-value="selectedFeatureId"
        :options="labeledFeatures"
        @update:model-value="onSelect"
    />
</template>

<style scoped>
.drawn-features-list {
    border: none;
}
</style>
