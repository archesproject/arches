<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";

import { useGettext } from "vue3-gettext";

import Select from "primevue/select";

import {
    DRAW_CREATE_EVENT,
    GEOMETRY_TYPE_LINESTRING,
    GEOMETRY_TYPE_POINT,
    GEOMETRY_TYPE_POLYGON,
    LINE,
    POINT,
    POLYGON,
} from "@/arches_vue_components/components/MapComponent/constants.ts";
import { useResolvedMapContext } from "@/arches_vue_components/components/MapComponent/composables/useMapContext.ts";

import type {
    DrawMode,
    MapContext,
} from "@/arches_vue_components/components/MapComponent/types.ts";

const { context = undefined } = defineProps<{
    context?: MapContext;
}>();

const { map, allowedGeometryTypes, selectedDrawnFeature, setDrawMode } =
    useResolvedMapContext(context, "DrawControls");

const { $gettext } = useGettext();

const selectedDrawType = ref<DrawMode | undefined>();

const geometryTypeToDrawType: Record<string, DrawMode> = {
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
    const types = allowedGeometryTypes.value;
    if (!types?.length) return allOptions;
    return allOptions.filter((opt) => types.includes(opt.code));
});

const displayDrawType = computed(() => {
    if (selectedDrawnFeature.value) {
        return geometryTypeToDrawType[selectedDrawnFeature.value.geometry.type];
    }
    return selectedDrawType.value;
});

onMounted(() => {
    map.value?.on(DRAW_CREATE_EVENT, clearDrawSelection);
});

onUnmounted(() => {
    map.value?.off(DRAW_CREATE_EVENT, clearDrawSelection);
});

function onDrawTypeSelected(type: DrawMode | undefined): void {
    selectedDrawType.value = type;
    setDrawMode(type ?? null);
}

function clearDrawSelection(): void {
    selectedDrawType.value = undefined;
}
</script>

<template>
    <div class="draw-controls">
        <label
            class="draw-controls-label"
            for="draw-type"
        >
            {{ $gettext("Draw type") }}
        </label>
        <Select
            id="draw-type"
            option-label="label"
            option-value="code"
            :model-value="displayDrawType"
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
}

.draw-controls-label {
    flex-shrink: 0;
    white-space: nowrap;
}
</style>
