<script setup lang="ts">
import { computed, ref } from "vue";

import { useGettext } from "vue3-gettext";

import Button from "openvue/button";
import Slider from "openvue/slider";

import OverlaySwatch from "@/arches_vue_components/components/MapComponent/components/OverlaySwatch.vue";

import { useResolvedMapContext } from "@/arches_vue_components/components/MapComponent/composables/useMapContext.ts";
import {
    getOverlayOpacityPercent,
    isOverlayOpacityAdjustable,
} from "@/arches_vue_components/components/MapComponent/utils/overlay-opacity.ts";

import type {
    MapContext,
    MapLayer,
} from "@/arches_vue_components/components/MapComponent/types.ts";

const TOGGLE_VISIBILITY_EVENT = "toggle-visibility" as const;
const DRAG_START_EVENT = "drag-start" as const;
const DRAG_END_EVENT = "drag-end" as const;

const {
    overlay,
    isReorderDisabled,
    isDragTarget,
    context = undefined,
} = defineProps<{
    overlay: MapLayer;
    isReorderDisabled: boolean;
    isDragTarget: boolean;
    context?: MapContext;
}>();

const emit = defineEmits<{
    (event: typeof TOGGLE_VISIBILITY_EVENT): void;
    (event: typeof DRAG_START_EVENT, dragEvent: DragEvent): void;
    (event: typeof DRAG_END_EVENT): void;
}>();

const { overlays, overlayOpacities, moveOverlay, setOverlayOpacity } =
    useResolvedMapContext(context, "OverlayRow");

const { $gettext } = useGettext();

const isOpacityExpanded = ref(false);

const opacityPercent = computed(() =>
    getOverlayOpacityPercent(overlayOpacities.value, overlay),
);

const isOpacityControlVisible = computed(
    () =>
        overlay.addtomap &&
        isOverlayOpacityAdjustable(overlay.layerdefinitions),
);

const overlayIndex = computed(() => overlays.value.indexOf(overlay));

const canMoveUp = computed(() => !isReorderDisabled && overlayIndex.value > 0);

const canMoveDown = computed(
    () => !isReorderDisabled && overlayIndex.value < overlays.value.length - 1,
);

function moveBy(offset: number): void {
    moveOverlay(overlay, overlayIndex.value + offset);
}

function updateOpacity(value: number | number[]): void {
    if (typeof value === "number") {
        setOverlayOpacity(overlay, value);
    }
}
</script>

<template>
    <div
        class="overlay-row"
        :class="{
            'overlay-row-off': !overlay.addtomap,
            'overlay-row-drag-target': isDragTarget,
        }"
    >
        <div class="overlay-row-main">
            <span
                class="overlay-drag-handle"
                aria-hidden="true"
                :class="{ 'overlay-drag-handle-disabled': isReorderDisabled }"
                :draggable="!isReorderDisabled"
                :title="$gettext('Drag to reorder')"
                @dragstart="emit(DRAG_START_EVENT, $event)"
                @dragend="emit(DRAG_END_EVENT)"
            >
                <i class="pi pi-bars" />
            </span>
            <div class="overlay-reorder-buttons">
                <Button
                    class="overlay-reorder-button"
                    icon="pi pi-angle-up"
                    size="small"
                    :text="true"
                    :disabled="!canMoveUp"
                    :aria-label="
                        $gettext('Move %{name} up', { name: overlay.name })
                    "
                    @click="moveBy(-1)"
                />
                <Button
                    class="overlay-reorder-button"
                    icon="pi pi-angle-down"
                    size="small"
                    :text="true"
                    :disabled="!canMoveDown"
                    :aria-label="
                        $gettext('Move %{name} down', { name: overlay.name })
                    "
                    @click="moveBy(1)"
                />
            </div>
            <Button
                class="overlay-visibility-toggle"
                :text="true"
                :aria-pressed="overlay.addtomap"
                @click="emit(TOGGLE_VISIBILITY_EVENT)"
            >
                <OverlaySwatch
                    :overlay="overlay"
                    :opacity-percent="opacityPercent"
                />
                <span
                    class="overlay-label"
                    :title="overlay.name"
                >
                    {{ overlay.name }}
                </span>
            </Button>
            <Button
                v-if="isOpacityControlVisible"
                class="overlay-opacity-button"
                size="small"
                :class="{
                    'overlay-opacity-button-collapsed': !isOpacityExpanded,
                }"
                :outlined="true"
                :rounded="true"
                :aria-expanded="isOpacityExpanded"
                :aria-label="
                    $gettext('Opacity settings for %{name}', {
                        name: overlay.name,
                    })
                "
                @click="isOpacityExpanded = !isOpacityExpanded"
            >
                <span>
                    {{
                        $gettext("%{percent}%", {
                            percent: String(opacityPercent),
                        })
                    }}
                </span>
                <i
                    class="pi pi-chevron-down overlay-opacity-chevron"
                    aria-hidden="true"
                />
            </Button>
        </div>
        <div
            v-if="isOpacityControlVisible && isOpacityExpanded"
            class="overlay-opacity"
        >
            <Slider
                class="overlay-opacity-slider"
                :model-value="opacityPercent"
                :min="0"
                :max="100"
                :aria-label="
                    $gettext('Opacity for %{name}', { name: overlay.name })
                "
                @update:model-value="updateOpacity"
            />
        </div>
    </div>
</template>

<style scoped>
.overlay-row {
    padding-block: 0.8rem;
    padding-inline: 1.1rem;
    border-block-end: 0.1rem solid var(--p-content-border-color);
}

.overlay-row:last-child {
    border-block-end: none;
}

.overlay-row:hover {
    background: var(--p-content-hover-background);
}

.overlay-row-off {
    background: var(--p-content-hover-background);
    color: var(--p-text-muted-color);
}

.overlay-row-drag-target {
    box-shadow: inset 0 0.3rem 0 var(--p-primary-color);
}

.overlay-row-main {
    display: flex;
    align-items: center;
    gap: 0.65rem;
}

.overlay-drag-handle {
    display: flex;
    flex: 0 0 auto;
    align-items: center;
    color: var(--p-text-muted-color);
    font-size: 1.35rem;
    cursor: grab;
}

.overlay-drag-handle:active {
    cursor: grabbing;
}

.overlay-drag-handle-disabled {
    opacity: 0.4;
    cursor: default;
}

.overlay-reorder-buttons {
    display: flex;
    flex: 0 0 auto;
    flex-direction: column;
}

.overlay-reorder-button {
    width: 2rem;
    height: 1.6rem;
    padding: 0;
}

.overlay-visibility-toggle {
    flex: 1;
    justify-content: flex-start;
    gap: 0.65rem;
    min-width: 0;
    padding: 0;
    color: inherit;
}

.overlay-label {
    flex: 1;
    text-align: start;
    min-width: 0;
    overflow: hidden;
    font-size: 1.35rem;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.overlay-opacity-button {
    flex: 0 0 auto;
    gap: 0.3rem;
    padding-block: 0.15rem;
    padding-inline: 0.55rem;
    font-size: 1.1rem;
    font-weight: 600;
}

.overlay-opacity-chevron {
    font-size: 1rem;
    transition: transform 0.15s ease;
}

.overlay-opacity-button-collapsed .overlay-opacity-chevron {
    transform: rotate(-90deg);
}

.overlay-opacity {
    display: flex;
    align-items: center;
    padding-block: 1.1rem 0.4rem;
    padding-inline: 1rem;
}

.overlay-opacity-slider {
    flex: 1;
}
</style>
