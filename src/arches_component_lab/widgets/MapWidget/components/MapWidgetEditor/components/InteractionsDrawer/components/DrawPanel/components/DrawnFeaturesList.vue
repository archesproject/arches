<script setup lang="ts">
import { computed, inject, ref } from "vue";
import type { Ref } from "vue";

import { useGettext } from "vue3-gettext";

import Listbox from "primevue/listbox";

import type { Feature } from "geojson";
import type { Map as MaplibreMap } from "maplibre-gl";

import {
    GEOMETRY_TYPE_LINESTRING,
    GEOMETRY_TYPE_POINT,
    GEOMETRY_TYPE_POLYGON,
    SIMPLE_SELECT,
} from "@/arches_component_lab/widgets/MapWidget/constants.ts";
import { getMapboxDraw } from "@/arches_component_lab/widgets/MapWidget/utils.ts";

const { map, features } = defineProps<{
    map: MaplibreMap;
    features: Feature[];
}>();

const selectedDrawnFeature = inject<Ref<Feature | null>>(
    "selectedDrawnFeature",
    ref(null),
);

const { $gettext } = useGettext();

const labeledFeatures = computed(() => {
    const countByType: Record<string, number> = {};

    return features.map((feature) => {
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

function onSelect(featureId: string) {
    const item = labeledFeatures.value.find(
        (item) => item.featureId === featureId,
    );
    if (!item) return;
    selectedDrawnFeature.value = item.feature;
    getMapboxDraw(map)?.changeMode(SIMPLE_SELECT, { featureIds: [featureId] });
}
</script>

<template>
    <Listbox
        v-if="features.length"
        :model-value="selectedFeatureId"
        :options="labeledFeatures"
        option-label="label"
        option-value="featureId"
        class="drawn-features-list"
        @update:model-value="onSelect"
    />
</template>

<style scoped>
.drawn-features-list {
    border: none;
    margin-block-end: 0.75rem;
}
</style>
