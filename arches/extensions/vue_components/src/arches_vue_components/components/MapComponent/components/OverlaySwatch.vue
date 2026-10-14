<script setup lang="ts">
import { computed } from "vue";

import { deriveOverlaySwatch } from "@/arches_vue_components/components/MapComponent/utils/overlay-swatch.ts";

import type { MapLayer } from "@/arches_vue_components/components/MapComponent/types.ts";

const { overlay, opacityPercent } = defineProps<{
    overlay: MapLayer;
    opacityPercent: number;
}>();

const swatch = computed(() => deriveOverlaySwatch(overlay));

const swatchStyle = computed(() => {
    const opacity = opacityPercent / 100;

    if (swatch.value?.kind === "gradient") {
        return {
            background: `linear-gradient(to right, ${swatch.value.colors.join(", ")})`,
            opacity,
        };
    }
    if (swatch.value?.kind === "icon" || !swatch.value) {
        return { opacity };
    }
    return { background: swatch.value.color, opacity };
});
</script>

<template>
    <i
        v-if="swatch?.kind === 'icon'"
        class="overlay-swatch-icon"
        aria-hidden="true"
        :class="swatch.iconClass"
        :style="swatchStyle"
    />
    <span
        v-else-if="swatch"
        class="overlay-swatch"
        aria-hidden="true"
        :class="swatch.kind"
        :style="swatchStyle"
    />
</template>

<style scoped>
.overlay-swatch {
    flex: 0 0 auto;
    width: 1.7rem;
    height: 1.7rem;
    border: 0.1rem solid var(--p-content-border-color);
    border-radius: 0.3rem;
}

.overlay-swatch.point {
    border-radius: 50%;
}

.overlay-swatch.line {
    align-self: center;
    height: 0.5rem;
    border: none;
}

.overlay-swatch.gradient {
    width: 2.6rem;
    border: none;
}

.overlay-swatch-icon {
    flex: 0 0 auto;
    width: 1.7rem;
    color: var(--p-text-muted-color);
    font-size: 1.4rem;
    text-align: center;
}
</style>
