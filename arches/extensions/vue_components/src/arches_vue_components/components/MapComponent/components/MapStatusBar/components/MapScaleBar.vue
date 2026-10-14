<script setup lang="ts">
import { onMounted, onUnmounted, useTemplateRef, watch } from "vue";

import * as maplibregl from "maplibre-gl";

import type { Map as MaplibreMap } from "maplibre-gl";

import type { MapScaleUnit } from "@/arches_vue_components/components/MapComponent/types.ts";

const SCALE_MAX_WIDTH_PIXELS = 100;

const { map, unit } = defineProps<{
    map: MaplibreMap;
    unit: MapScaleUnit;
}>();

const scaleContainer = useTemplateRef<HTMLDivElement>("scaleContainer");

const scaleControl = new maplibregl.ScaleControl({
    maxWidth: SCALE_MAX_WIDTH_PIXELS,
    unit,
});

watch(
    () => unit,
    (newUnit) => {
        scaleControl.setUnit(newUnit);
    },
);

onMounted(() => {
    scaleContainer.value!.appendChild(scaleControl.onAdd(map));
});

onUnmounted(() => {
    scaleControl.onRemove();
});
</script>

<template>
    <div
        ref="scaleContainer"
        class="map-scale-bar"
    />
</template>

<style scoped>
.map-scale-bar {
    display: flex;
    align-items: center;
}

.map-scale-bar :deep(.maplibregl-ctrl-scale) {
    padding-block: 0.5rem 0;
    padding-inline: 0.5rem;
    background: none;
    border: none;
    border-block-start: 0.1rem solid var(--p-text-muted-color);
    color: var(--p-text-muted-color);
    font-size: 1.1rem;
}
</style>
