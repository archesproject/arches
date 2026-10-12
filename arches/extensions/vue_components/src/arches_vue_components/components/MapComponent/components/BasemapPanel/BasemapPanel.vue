<script setup lang="ts">
import { onMounted, ref, useTemplateRef } from "vue";

import { useGettext } from "vue3-gettext";

import Button from "openvue/button";

import { renderBasemapThumbnail } from "@/arches_vue_components/components/MapComponent/components/BasemapPanel/utils/basemap-thumbnail.ts";
import { useResolvedMapContext } from "@/arches_vue_components/components/MapComponent/composables/useMapContext.ts";

import type {
    Basemap,
    MapContext,
} from "@/arches_vue_components/components/MapComponent/types.ts";

const { context = undefined } = defineProps<{
    context?: MapContext;
}>();

const { map, basemaps } = useResolvedMapContext(context, "BasemapPanel");

const { $gettext } = useGettext();

const thumbnailRenderContainer = useTemplateRef<HTMLDivElement>(
    "thumbnailRenderContainer",
);
const thumbnailsByUrl = ref<Record<string, string | null>>({});

onMounted(async () => {
    if (!map.value) {
        return;
    }

    const center = map.value.getCenter();
    const zoom = map.value.getZoom();

    for (const basemap of basemaps.value) {
        if (!thumbnailRenderContainer.value) {
            return;
        }
        thumbnailsByUrl.value[basemap.url] = await renderBasemapThumbnail(
            thumbnailRenderContainer.value,
            basemap.url,
            center,
            zoom,
        );
    }
});

function selectBasemap(selectedBasemap: Basemap): void {
    for (const basemap of basemaps.value) {
        basemap.active = basemap === selectedBasemap;
    }
}
</script>

<template>
    <div class="basemap-grid">
        <Button
            v-for="basemap in basemaps"
            :key="basemap.id"
            class="basemap-card"
            :class="{ 'basemap-card-active': basemap.active }"
            :text="true"
            :aria-pressed="basemap.active"
            @click="selectBasemap(basemap)"
        >
            <span class="basemap-thumbnail">
                <img
                    v-if="thumbnailsByUrl[basemap.url]"
                    :src="thumbnailsByUrl[basemap.url] ?? undefined"
                    :alt="$gettext('%{name} preview', { name: basemap.name })"
                />
                <i
                    v-else-if="thumbnailsByUrl[basemap.url] === null"
                    class="pi pi-image basemap-thumbnail-placeholder"
                    aria-hidden="true"
                />
                <i
                    v-else
                    class="pi pi-spin pi-spinner basemap-thumbnail-placeholder"
                    aria-hidden="true"
                />
                <span
                    v-if="basemap.active"
                    class="basemap-check"
                >
                    <i
                        class="pi pi-check"
                        aria-hidden="true"
                    />
                </span>
            </span>
            <span class="basemap-name">{{ basemap.name }}</span>
        </Button>
        <div
            class="basemap-thumbnail-renderer"
            aria-hidden="true"
        >
            <div
                ref="thumbnailRenderContainer"
                class="basemap-thumbnail-render-container"
            />
        </div>
    </div>
</template>

<style scoped>
.basemap-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.1rem;
    padding: 1.45rem;
}

.basemap-card {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 0;
    padding: 0;
    overflow: hidden;
    background: var(--p-content-background);
    border: 0.2rem solid var(--p-content-border-color);
    border-radius: 0.4rem;
    color: var(--p-text-color);
}

.basemap-card.basemap-card-active {
    border-color: var(--p-primary-color);
}

.basemap-thumbnail {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 9.9rem;
    background: var(--p-content-hover-background);
}

.basemap-thumbnail img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.basemap-thumbnail-placeholder {
    color: var(--p-text-muted-color);
    font-size: 1.75rem;
}

.basemap-check {
    position: absolute;
    inset-block-start: 0.4rem;
    inset-inline-end: 0.4rem;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 1.75rem;
    height: 1.75rem;
    border-radius: 50%;
    background: var(--p-primary-color);
    color: var(--p-primary-contrast-color);
    font-size: 1rem;
}

.basemap-name {
    padding-block: 0.65rem;
    padding-inline: 0.8rem;
    font-size: 1.25rem;
    font-weight: 600;
    text-align: center;
}

.basemap-thumbnail-renderer {
    position: absolute;
    width: 0;
    height: 0;
    overflow: hidden;
}

.basemap-thumbnail-render-container {
    width: 24rem;
    height: 16rem;
}
</style>
