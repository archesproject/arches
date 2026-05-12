<script setup lang="ts">
import { computed, inject, onMounted, onUnmounted, ref } from "vue";
import type { ComputedRef, Ref } from "vue";

import { useGettext } from "vue3-gettext";

import Select from "primevue/select";

import type { Feature } from "geojson";
import type { Map as MaplibreMap } from "maplibre-gl";

import {
    DRAW_CREATE_EVENT,
    DRAW_LINE_STRING,
    DRAW_POINT,
    DRAW_POLYGON,
    GEOMETRY_TYPE_LINESTRING,
    GEOMETRY_TYPE_POINT,
    GEOMETRY_TYPE_POLYGON,
    LINE,
    POINT,
    POLYGON,
} from "@/arches_component_lab/widgets/MapWidget/constants.ts";
import { getMapboxDraw } from "@/arches_component_lab/widgets/MapWidget/utils.ts";

const { map } = defineProps<{
    map: MaplibreMap;
}>();

defineExpose({
    deleteSelectedDrawnFeature,
    deleteAllDrawnFeatures,
});

const { $gettext } = useGettext();

const geometryTypes = inject<
    Ref<string[] | null> | ComputedRef<string[] | null>
>("geometryTypes", ref(null));
const selectedDrawnFeature = inject<Ref<Feature | null>>(
    "selectedDrawnFeature",
    ref(null),
);

const selectedDrawType = ref<string | undefined>();

const geometryTypeToDrawType: Record<string, string> = {
    [GEOMETRY_TYPE_POINT]: POINT,
    [GEOMETRY_TYPE_LINESTRING]: LINE,
    [GEOMETRY_TYPE_POLYGON]: POLYGON,
};

const allOptions = [
    { label: $gettext("Draw a Marker"), code: POINT },
    { label: $gettext("Draw a Polyline"), code: LINE },
    { label: $gettext("Draw a Polygon"), code: POLYGON },
];

const options = computed(() => {
    const types = geometryTypes.value;
    if (!types?.length) return allOptions;
    return allOptions.filter((opt) => types.includes(opt.code));
});

const displayDrawType = computed(() => {
    if (selectedDrawnFeature.value) {
        return geometryTypeToDrawType[selectedDrawnFeature.value.geometry.type];
    }
    return selectedDrawType.value;
});

function onDrawTypeSelected(type: string | undefined) {
    selectedDrawType.value = type;
    const draw = getMapboxDraw(map);

    if (!type || !draw) {
        map.getCanvas().style.cursor = "";
        return;
    }

    map.getCanvas().style.cursor = "crosshair";

    if (type === POINT) {
        draw.changeMode(DRAW_POINT);
    } else if (type === LINE) {
        draw.changeMode(DRAW_LINE_STRING);
    } else if (type === POLYGON) {
        draw.changeMode(DRAW_POLYGON);
    }
}

function clearDrawSelection() {
    selectedDrawType.value = undefined;
    map.getCanvas().style.cursor = "";
}

onMounted(() => {
    map.on(DRAW_CREATE_EVENT, clearDrawSelection);
});

onUnmounted(() => {
    map.off(DRAW_CREATE_EVENT, clearDrawSelection);
});

function deleteAllDrawnFeatures() {
    const draw = getMapboxDraw(map);
    if (!draw) return;

    draw.deleteAll();
    map.fire("draw.delete");
}

function deleteSelectedDrawnFeature() {
    const draw = getMapboxDraw(map);
    if (!draw) return;

    const selectedFeatures = draw.getSelected();
    if (selectedFeatures.features.length) {
        draw.delete(selectedFeatures.features[0].id);
        map.fire("draw.delete");
    }
}
</script>

<template>
    <div class="draw-controls">
        <label for="draw-type">{{ $gettext("Draw type") }}</label>
        <Select
            id="draw-type"
            :model-value="displayDrawType"
            option-label="label"
            option-value="code"
            :options="options"
            :placeholder="$gettext('Draw a shape')"
            :disabled="selectedDrawnFeature !== null"
            :fluid="true"
            @update:model-value="onDrawTypeSelected"
        />
    </div>
</template>

<style scoped>
.draw-controls {
    align-items: baseline;
    display: flex;
    flex-direction: row;
    gap: 1rem;
    margin-block-start: 0.9375rem;
}
</style>
