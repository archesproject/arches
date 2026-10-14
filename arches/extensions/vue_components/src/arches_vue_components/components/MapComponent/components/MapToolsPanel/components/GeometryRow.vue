<script setup lang="ts">
import { computed, onUnmounted, ref, useId, watch } from "vue";

import { debounce } from "es-toolkit";
import { useGettext } from "vue3-gettext";

import Button from "openvue/button";
import InputNumber from "openvue/inputnumber";
import Select from "openvue/select";

import {
    BUFFER_INPUT_DEBOUNCE_MILLISECONDS,
    DEFAULT_BUFFER_DISTANCE,
    FEET,
    GEOMETRY_ICON_BY_TYPE,
    KILOMETERS,
    METERS,
    MILES,
    YARDS,
} from "@/arches_vue_components/components/MapComponent/constants.ts";

import { useResolvedMapContext } from "@/arches_vue_components/components/MapComponent/composables/useMapContext.ts";

import type { Feature } from "geojson";
import type { InputNumberInputEvent } from "openvue/inputnumber";

import type { MapContext } from "@/arches_vue_components/components/MapComponent/types.ts";

const EDIT_COORDINATES_EVENT = "edit-coordinates" as const;
const SINGLE_PART_GEOMETRY_TYPES = ["Point", "LineString", "Polygon"];

const {
    feature,
    label,
    isSelected,
    context = undefined,
} = defineProps<{
    feature: Feature;
    label: string;
    isSelected: boolean;
    context?: MapContext;
}>();

const emit = defineEmits<{
    (event: typeof EDIT_COORDINATES_EVENT, featureId: string): void;
}>();

const {
    selectDrawnFeature,
    editDrawnFeature,
    deleteDrawnFeature,
    setBufferForFeature,
    fitToFeatures,
} = useResolvedMapContext(context, "GeometryRow");

const { $gettext } = useGettext();

const bufferControlsId = useId();

const bufferDistance = ref<number | null>(
    feature.properties?.buffer_distance || DEFAULT_BUFFER_DISTANCE,
);
const bufferUnits = ref<string>(feature.properties?.buffer_units ?? METERS);
const isBufferOn = ref(feature.properties?.buffer_distance > 0);
const areBufferControlsVisible = ref(true);

const applyBufferDebounced = debounce(
    applyBuffer,
    BUFFER_INPUT_DEBOUNCE_MILLISECONDS,
);

const unitOptions = [
    { label: $gettext("Meters"), value: METERS },
    { label: $gettext("Kilometers"), value: KILOMETERS },
    { label: $gettext("Feet"), value: FEET },
    { label: $gettext("Miles"), value: MILES },
    { label: $gettext("Yards"), value: YARDS },
];

const iconClass = computed(
    () => GEOMETRY_ICON_BY_TYPE[feature.geometry.type] ?? "pi pi-question",
);

const canEditCoordinates = computed(() =>
    SINGLE_PART_GEOMETRY_TYPES.includes(feature.geometry.type),
);

const bufferToggleLabel = computed(() => {
    if (isBufferOn.value) {
        return $gettext("Remove buffer from %{label}", { label });
    }
    return $gettext("Apply buffer to %{label}", { label });
});

watch([bufferDistance, bufferUnits], () => {
    if (isBufferOn.value) {
        applyBufferDebounced();
    }
});

onUnmounted(() => {
    applyBufferDebounced.flush();
});

function applyBuffer(): void {
    setBufferForFeature(feature, bufferDistance.value ?? 0, bufferUnits.value);
}

function updateBufferDistance(event: InputNumberInputEvent): void {
    bufferDistance.value = typeof event.value === "number" ? event.value : null;
}

function toggleBuffer(): void {
    selectFeature();
    applyBufferDebounced.cancel();
    isBufferOn.value = !isBufferOn.value;

    if (!isBufferOn.value) {
        setBufferForFeature(feature, 0, bufferUnits.value);
        return;
    }
    areBufferControlsVisible.value = true;
    applyBuffer();
}

function selectFeature(): void {
    selectDrawnFeature(feature);
    fitToFeatures([feature]);
}

function editFeature(): void {
    editDrawnFeature(feature);
    fitToFeatures([feature]);
}
</script>

<template>
    <div
        class="geometry-row"
        :class="{ 'geometry-row-selected': isSelected }"
    >
        <div class="geometry-row-main">
            <Button
                class="geometry-row-select"
                :text="true"
                :aria-pressed="isSelected"
                @click="selectFeature"
            >
                <i
                    class="geometry-row-icon"
                    aria-hidden="true"
                    :class="iconClass"
                />
                <span
                    class="geometry-row-label"
                    :title="label"
                >
                    {{ label }}
                </span>
            </Button>
            <Button
                v-if="isBufferOn"
                class="geometry-buffer-disclosure"
                icon="pi pi-chevron-down"
                severity="secondary"
                size="small"
                :class="{
                    'geometry-buffer-disclosure-collapsed':
                        !areBufferControlsVisible,
                }"
                :aria-expanded="areBufferControlsVisible"
                :aria-controls="bufferControlsId"
                :aria-label="
                    $gettext('Buffer settings for %{label}', { label })
                "
                @click="areBufferControlsVisible = !areBufferControlsVisible"
            />
            <Button
                class="geometry-buffer-toggle"
                size="small"
                :label="$gettext('Buffer')"
                :text="!isBufferOn"
                :rounded="true"
                :aria-pressed="isBufferOn"
                :aria-label="bufferToggleLabel"
                :title="bufferToggleLabel"
                @click="toggleBuffer"
            />
            <Button
                class="geometry-link-button"
                size="small"
                :label="$gettext('Edit')"
                :link="true"
                :aria-label="$gettext('Edit %{label}', { label })"
                @click="editFeature"
            />
            <Button
                v-if="canEditCoordinates"
                class="geometry-link-button"
                size="small"
                :label="$gettext('Coordinates')"
                :link="true"
                :aria-label="
                    $gettext('Edit coordinates for %{label}', { label })
                "
                @click="emit(EDIT_COORDINATES_EVENT, String(feature.id))"
            />
            <Button
                class="geometry-delete-button"
                icon="pi pi-trash"
                :title="$gettext('Delete')"
                severity="secondary"
                size="small"
                :aria-label="$gettext('Delete %{label}', { label })"
                @click="deleteDrawnFeature(feature)"
            />
        </div>
        <div
            v-if="isBufferOn && areBufferControlsVisible"
            :id="bufferControlsId"
            class="geometry-buffer-controls"
        >
            <InputNumber
                v-model="bufferDistance"
                class="geometry-buffer-distance"
                size="small"
                :min="0"
                :aria-label="
                    $gettext('Buffer distance for %{label}', { label })
                "
                @input="updateBufferDistance"
            />
            <Select
                v-model="bufferUnits"
                class="geometry-buffer-units"
                option-label="label"
                option-value="value"
                append-to="self"
                size="small"
                :options="unitOptions"
                :aria-label="$gettext('Buffer unit for %{label}', { label })"
            />
        </div>
    </div>
</template>

<style scoped>
.geometry-row {
    display: flex;
    flex-direction: column;
    gap: 0.65rem;
    padding-block: 0.8rem;
    padding-inline: 0.95rem;
    border-block-end: 0.1rem solid var(--p-content-border-color);
    border-inline-start: 0.3rem solid transparent;
}

.geometry-row:last-child {
    border-block-end: none;
}

.geometry-row:hover {
    background: var(--p-content-hover-background);
}

.geometry-row-selected {
    border-inline-start-color: var(--p-primary-color);
}

.geometry-row-main {
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.geometry-row-select {
    flex: 1;
    justify-content: flex-start;
    gap: 0.4rem;
    min-width: 0;
    padding: 0;
    color: inherit;
}

.geometry-row-icon {
    flex: 0 0 auto;
    color: var(--p-primary-color);
    font-size: 1.35rem;
}

.geometry-row-label {
    flex: 1;
    text-align: start;
    min-width: 0;
    overflow: hidden;
    font-size: 1.3rem;
    font-weight: 600;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.geometry-buffer-disclosure,
.geometry-delete-button {
    flex: 0 0 auto;
    width: 2.4rem;
    height: 2.4rem;
    padding: 0;
}

.geometry-buffer-disclosure :deep(.p-button-icon) {
    font-size: 1.1rem;
    transition: transform 0.15s ease;
}

.geometry-buffer-disclosure-collapsed :deep(.p-button-icon) {
    transform: rotate(-90deg);
}

.geometry-buffer-toggle {
    flex: 0 0 auto;
    padding-block: 0.25rem;
    padding-inline: 0.8rem;
}

.geometry-link-button {
    flex: 0 0 auto;
    padding-block: 0;
    padding-inline: 0.25rem;
}

.geometry-buffer-controls {
    display: flex;
    align-items: center;
    gap: 0.65rem;
}

.geometry-buffer-distance {
    width: 8rem;
}

.geometry-buffer-units {
    flex: 1;
}
</style>
