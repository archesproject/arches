<script setup lang="ts">
import { inject, ref, watch } from "vue";
import type { Ref } from "vue";

import MapboxDraw from "@mapbox/mapbox-gl-draw";
import { useGettext } from "vue3-gettext";

import InputNumber from "primevue/inputnumber";
import Panel from "primevue/panel";
import Select from "primevue/select";

import type { Feature } from "geojson";
import type { Map as MaplibreMap } from "maplibre-gl";

import {
    DRAW_UPDATE_EVENT,
    FEET,
    KILOMETERS,
    METERS,
    MILES,
    YARDS,
} from "@/arches_component_lab/widgets/MapWidget/constants.ts";

const { map } = defineProps<{
    map: MaplibreMap;
}>();

const { $gettext } = useGettext();

const selectedDrawnFeature = inject<Ref<Feature | null>>(
    "selectedDrawnFeature",
    ref(null),
);

const bufferDistance = ref(0);
const selectedUnits = ref(METERS);

const unitOptions = [
    { label: $gettext("meters"), code: METERS },
    { label: $gettext("feet"), code: FEET },
    { label: $gettext("miles"), code: MILES },
    { label: $gettext("kilometers"), code: KILOMETERS },
    { label: $gettext("yards"), code: YARDS },
];

watch([bufferDistance, selectedUnits], () => {
    if (bufferDistance.value < 0) {
        bufferDistance.value = 0;
    }

    const feature = selectedDrawnFeature.value;
    if (!feature) return;

    const draw = map._controls.find(
        (control: unknown) => control instanceof MapboxDraw,
    ) as InstanceType<typeof MapboxDraw>;

    feature.properties!.buffer_distance = bufferDistance.value;
    feature.properties!.buffer_units = selectedUnits.value;

    draw.add(feature);
    map.fire(DRAW_UPDATE_EVENT, { features: [feature] });
});

watch(
    selectedDrawnFeature,
    (feature) => {
        if (
            feature &&
            Number.isInteger(feature.properties?.buffer_distance) &&
            feature.properties?.buffer_units
        ) {
            bufferDistance.value = feature.properties.buffer_distance;
            selectedUnits.value = feature.properties.buffer_units;
            return;
        }

        bufferDistance.value = 0;
        selectedUnits.value = METERS;
    },
    { immediate: true },
);
</script>

<template>
    <Panel
        class="buffer-controls-panel"
        :pt="{ title: { style: { 'font-weight': 500 } } }"
        :header="$gettext('Buffer Selected Feature')"
    >
        <div class="buffer-controls">
            <label for="buff-distance">{{ $gettext("Distance") }}</label>
            <InputNumber
                id="buff-distance"
                v-model="bufferDistance"
                :min="0"
                :input-style="{ fontSize: '1.4rem' }"
                :fluid="true"
            />
            <Select
                id="buff-units"
                v-model="selectedUnits"
                :options="unitOptions"
                option-value="code"
                option-label="label"
                :placeholder="$gettext('Units')"
                :fluid="true"
            />
        </div>
    </Panel>
</template>

<style scoped>
.buffer-controls-panel {
    margin-block-start: 0.75rem;
}

.buffer-controls {
    align-items: baseline;
    display: flex;
    flex-direction: row;
    gap: 1rem;
}
</style>
