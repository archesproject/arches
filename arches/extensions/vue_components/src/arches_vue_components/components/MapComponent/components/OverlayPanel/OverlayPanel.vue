<script setup lang="ts">
import { computed, ref } from "vue";

import { useGettext } from "vue3-gettext";

import Button from "openvue/button";
import InputText from "openvue/inputtext";

import OverlayRow from "@/arches_vue_components/components/MapComponent/components/OverlayPanel/components/OverlayRow.vue";

import { useResolvedMapContext } from "@/arches_vue_components/components/MapComponent/composables/useMapContext.ts";

import type {
    MapContext,
    MapLayer,
} from "@/arches_vue_components/components/MapComponent/types.ts";

const { context = undefined } = defineProps<{
    context?: MapContext;
}>();

const resolvedContext = useResolvedMapContext(context, "OverlayPanel");
const { overlays, moveOverlay } = resolvedContext;

const { $gettext } = useGettext();

const filterText = ref("");
const draggedOverlay = ref<MapLayer | null>(null);
const dragTargetOverlayId = ref<string | null>(null);

const isFiltering = computed(() => filterText.value.trim() !== "");

const filteredOverlays = computed(() => {
    const normalizedFilter = filterText.value.trim().toLowerCase();
    return overlays.value.filter((overlay) =>
        overlay.name.toLowerCase().includes(normalizedFilter),
    );
});

function toggleOverlayVisibility(overlay: MapLayer): void {
    overlay.addtomap = !overlay.addtomap;
}

function startDrag(dragEvent: DragEvent, overlay: MapLayer): void {
    draggedOverlay.value = overlay;
    if (dragEvent.dataTransfer) {
        dragEvent.dataTransfer.effectAllowed = "move";
        dragEvent.dataTransfer.setData("text/plain", overlay.maplayerid);
    }
}

function handleDragOver(dragEvent: DragEvent, overlay: MapLayer): void {
    if (!draggedOverlay.value || draggedOverlay.value === overlay) {
        return;
    }

    dragEvent.preventDefault();
    dragTargetOverlayId.value = overlay.maplayerid;
}

function handleDragLeave(overlay: MapLayer): void {
    if (dragTargetOverlayId.value === overlay.maplayerid) {
        dragTargetOverlayId.value = null;
    }
}

function handleDrop(targetOverlay: MapLayer): void {
    const overlayToMove = draggedOverlay.value;
    endDrag();
    if (!overlayToMove || overlayToMove === targetOverlay) {
        return;
    }

    const remainingOverlays = overlays.value.filter(
        (overlay) => overlay !== overlayToMove,
    );
    moveOverlay(overlayToMove, remainingOverlays.indexOf(targetOverlay));
}

function endDrag(): void {
    draggedOverlay.value = null;
    dragTargetOverlayId.value = null;
}
</script>

<template>
    <div class="overlay-filter">
        <div class="overlay-filter-row">
            <InputText
                v-model="filterText"
                class="overlay-filter-input"
                :placeholder="$gettext('Filter overlays...')"
                :aria-label="$gettext('Filter overlays')"
                :fluid="true"
            />
            <Button
                v-if="isFiltering"
                icon="pi pi-times"
                severity="secondary"
                size="small"
                :text="true"
                :aria-label="$gettext('Clear overlay filter')"
                @click="filterText = ''"
            />
        </div>
        <p
            v-if="isFiltering"
            class="overlay-reorder-hint"
        >
            {{ $gettext("Clear the filter to reorder overlays.") }}
        </p>
    </div>
    <div class="overlay-list">
        <OverlayRow
            v-for="overlay in filteredOverlays"
            :key="overlay.maplayerid"
            :overlay="overlay"
            :is-reorder-disabled="isFiltering"
            :is-drag-target="dragTargetOverlayId === overlay.maplayerid"
            :context="resolvedContext"
            @toggle-visibility="toggleOverlayVisibility(overlay)"
            @drag-start="startDrag($event, overlay)"
            @drag-end="endDrag"
            @dragover="handleDragOver($event, overlay)"
            @dragleave="handleDragLeave(overlay)"
            @drop.prevent="handleDrop(overlay)"
        />
    </div>
    <div
        v-if="!filteredOverlays.length"
        class="overlay-empty"
    >
        <span v-if="isFiltering">
            {{
                $gettext('No overlays match "%{filter}"', {
                    filter: filterText,
                })
            }}
        </span>
        <span v-else>{{ $gettext("No overlays are available.") }}</span>
    </div>
</template>

<style scoped>
.overlay-filter {
    display: flex;
    flex: 0 0 auto;
    flex-direction: column;
    gap: 0.55rem;
    padding-block: 1.1rem 0.8rem;
    padding-inline: 1.45rem;
}

.overlay-filter-row {
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

.overlay-filter-input {
    font-size: 1.3rem;
}

.overlay-reorder-hint {
    margin: 0;
    color: var(--p-text-muted-color);
    font-size: 1.1rem;
}

.overlay-empty {
    padding: 1.6rem;
    color: var(--p-text-muted-color);
    font-size: 1.3rem;
    text-align: center;
}
</style>
