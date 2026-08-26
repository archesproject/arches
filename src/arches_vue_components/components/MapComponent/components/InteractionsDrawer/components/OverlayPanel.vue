<script setup lang="ts">
import ToggleSwitch from "primevue/toggleswitch";

import { useResolvedMapContext } from "@/arches_vue_components/components/MapComponent/composables/useMapContext.ts";

import type { MapContext } from "@/arches_vue_components/components/MapComponent/types.ts";

const { context = undefined } = defineProps<{
    context?: MapContext;
}>();

const { overlays } = useResolvedMapContext(context, "OverlayPanel");
</script>

<template>
    <div
        v-for="overlay in overlays"
        :key="overlay.id"
    >
        <div
            class="overlay-item"
            @click="overlay.addtomap = !overlay.addtomap"
        >
            <ToggleSwitch
                v-model="overlay.addtomap"
                @click.stop
            />
            <label>{{ overlay.name }}</label>
        </div>
    </div>
</template>

<style scoped>
.overlay-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1.5rem;
    border-block-end: 0.0625rem solid var(--p-content-border-color);
    cursor: pointer;
}

.overlay-item label {
    line-height: 1;
    margin-block-end: 0;
    cursor: pointer;
}

.overlay-item:hover {
    background: var(--p-button-secondary-hover-background);
}
</style>
