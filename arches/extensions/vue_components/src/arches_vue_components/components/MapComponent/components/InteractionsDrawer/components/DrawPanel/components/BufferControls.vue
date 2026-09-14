<script setup lang="ts">
import { ref, watch } from "vue";

import { useGettext } from "vue3-gettext";

import InputNumber from "primevue/inputnumber";
import Panel from "primevue/panel";
import Select from "primevue/select";

import {
    FEET,
    KILOMETERS,
    METERS,
    MILES,
    YARDS,
} from "@/arches_vue_components/components/MapComponent/constants.ts";
import { useResolvedMapContext } from "@/arches_vue_components/components/MapComponent/composables/useMapContext.ts";

import type { MapContext } from "@/arches_vue_components/components/MapComponent/types.ts";

const { context = undefined } = defineProps<{
    context?: MapContext;
}>();

const { selectedDrawnFeature, setBufferForSelectedFeature } =
    useResolvedMapContext(context, "BufferControls");

const { $gettext } = useGettext();

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

    if (!selectedDrawnFeature.value) return;

    setBufferForSelectedFeature(bufferDistance.value, selectedUnits.value);
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
        :pt="{ title: { style: { 'font-weight': 500 } } }"
        :header="$gettext('Buffer Selected Feature')"
    >
        <div class="buffer-controls">
            <label
                class="buffer-controls-label"
                for="buff-distance"
            >
                {{ $gettext("Distance") }}
            </label>
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
                option-value="code"
                option-label="label"
                :options="unitOptions"
                :placeholder="$gettext('Units')"
                :fluid="true"
            />
        </div>
    </Panel>
</template>

<style scoped>
.buffer-controls {
    align-items: baseline;
    display: flex;
    flex-direction: row;
    gap: 1rem;
}

.buffer-controls-label {
    flex-shrink: 0;
    white-space: nowrap;
}
</style>
