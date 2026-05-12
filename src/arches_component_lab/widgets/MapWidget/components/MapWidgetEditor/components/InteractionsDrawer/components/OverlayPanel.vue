<script setup lang="ts">
import { inject, ref } from "vue";

import ToggleSwitch from "primevue/toggleswitch";

import type { Map } from "maplibre-gl";
import type { PropType, Ref } from "vue";

import type { MapLayer } from "@/arches_component_lab/widgets/MapWidget/types.ts";

defineProps({
    map: {
        type: Object as PropType<Map>,
        required: true,
    },
});

const overlays = inject<Ref<MapLayer[]>>("overlays", ref([]));
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
