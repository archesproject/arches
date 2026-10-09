<script setup lang="ts">
import { computed, inject, onUnmounted, ref, watch } from "vue";

import { useGettext } from "vue3-gettext";

import Button from "openvue/button";
import Skeleton from "openvue/skeleton";
import Tag from "openvue/tag";

import { generateArchesURL } from "@/arches_vue_components/application/generate-arches-url.ts";
import { fetchResourceDescriptor } from "@/arches_vue_components/components/MapComponent/api.ts";
import { mapContextKey } from "@/arches_vue_components/components/MapComponent/composables/useMapContext.ts";

import type { Feature } from "geojson";

import type {
    MapContext,
    ResourceDescriptor,
} from "@/arches_vue_components/components/MapComponent/types.ts";

const { features, context = undefined } = defineProps<{
    features: Feature[];
    context?: MapContext;
}>();

const resolvedContext = context ?? inject(mapContextKey, null);

const { $gettext } = useGettext();

const index = ref(0);
const isLoading = ref(false);
const descriptor = ref<ResourceDescriptor | null>(null);

let isUnmounted = false;

const feature = computed(() => features[index.value]);
const resourceId = computed(
    () => feature.value?.properties?.resourceinstanceid ?? null,
);
const total = computed(() => features.length);
const isFirstLoad = computed(
    () => isLoading.value && descriptor.value === null,
);
const isShowingStaleContent = computed(
    () => isLoading.value && descriptor.value !== null,
);

watch(
    () => features,
    () => {
        index.value = 0;
    },
);

watch(
    resourceId,
    async (id) => {
        if (!id) {
            descriptor.value = null;
            resolvedContext?.clearFeatureHighlight();
            return;
        }
        isLoading.value = true;
        try {
            const fetchedDescriptor = await fetchResourceDescriptor(id);
            if (isUnmounted || id !== resourceId.value) {
                return;
            }
            descriptor.value = fetchedDescriptor;
            resolvedContext?.showFeatureHighlight(
                fetchedDescriptor.geometries.flatMap((descriptorGeometry) =>
                    descriptorGeometry.geom.features.map(
                        (geometryFeature) => geometryFeature.geometry,
                    ),
                ),
            );
        } catch (error) {
            descriptor.value = null;
            resolvedContext?.clearFeatureHighlight();
            console.error("Error fetching resource descriptor:", error);
        } finally {
            if (id === resourceId.value) {
                isLoading.value = false;
            }
        }
    },
    { immediate: true },
);

onUnmounted(() => {
    isUnmounted = true;
});

function navigateToPreviousFeature(): void {
    index.value = (index.value - 1 + total.value) % total.value;
}

function navigateToNextFeature(): void {
    index.value = (index.value + 1) % total.value;
}
</script>

<template>
    <div class="popup">
        <div class="popup-pager">
            <span class="popup-pager-count">
                {{
                    $gettext("%{current} of %{total}", {
                        current: String(index + 1),
                        total: String(total),
                    })
                }}
            </span>
            <div class="popup-pager-actions">
                <template v-if="total > 1">
                    <Button
                        class="popup-pager-button"
                        icon="pi pi-chevron-left"
                        :rounded="true"
                        :aria-label="$gettext('Previous feature')"
                        @click="navigateToPreviousFeature"
                    />
                    <Button
                        class="popup-pager-button"
                        icon="pi pi-chevron-right"
                        :rounded="true"
                        :aria-label="$gettext('Next feature')"
                        @click="navigateToNextFeature"
                    />
                </template>
                <Button
                    v-if="resolvedContext"
                    class="popup-pager-button"
                    icon="pi pi-times"
                    :rounded="true"
                    :aria-label="$gettext('Close')"
                    @click="resolvedContext.closeFeaturePopup"
                />
            </div>
        </div>

        <div
            class="popup-content"
            :class="{ 'popup-content-stale': isShowingStaleContent }"
            :aria-busy="isLoading"
        >
            <div class="popup-header">
                <Skeleton
                    v-if="isFirstLoad"
                    height="1.6rem"
                    width="60%"
                />
                <template v-else>
                    <div class="popup-title">
                        {{ descriptor?.displayname ?? resourceId }}
                    </div>
                    <div
                        v-if="descriptor"
                        class="popup-badges"
                    >
                        <Tag
                            v-if="descriptor.graph_name"
                            class="popup-model-badge"
                            severity="secondary"
                            :icon="descriptor.graph_iconclass ?? undefined"
                            :value="descriptor.graph_name"
                            :rounded="true"
                        />
                        <Tag
                            v-if="descriptor.lifecycle_state"
                            class="popup-status-badge"
                            severity="info"
                            :value="descriptor.lifecycle_state"
                            :rounded="true"
                        />
                    </div>
                </template>
            </div>

            <div
                v-if="isFirstLoad"
                class="popup-body"
            >
                <Skeleton height="1.6rem" />
                <Skeleton
                    height="1.6rem"
                    width="80%"
                />
            </div>
            <template v-else-if="descriptor">
                <!-- eslint-disable vue/no-v-html -->
                <div
                    v-if="descriptor.map_popup"
                    class="popup-body popup-html-content"
                    v-html="descriptor.map_popup"
                />
                <!-- eslint-enable vue/no-v-html -->
                <div
                    v-if="descriptor.displaydescription"
                    class="popup-snippet-section"
                >
                    <p class="popup-snippet">
                        {{ descriptor.displaydescription }}
                    </p>
                </div>
            </template>
        </div>

        <div
            v-if="resourceId"
            class="popup-footer"
        >
            <Button
                class="popup-footer-link"
                as="a"
                target="_blank"
                icon="pi pi-book"
                size="small"
                :href="
                    generateArchesURL('arches:resource_report', {
                        resourceid: resourceId,
                    })
                "
                :label="$gettext('Report')"
                :link="true"
            />
        </div>
    </div>
</template>

<style scoped>
.popup {
    display: flex;
    flex-direction: column;
    height: 100%;
    font-size: 1.35rem;
}

.popup-pager {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.95rem;
    min-height: 3rem;
    padding-block: 0.55rem;
    padding-inline: 0.95rem;
    background: var(--p-primary-color);
    color: var(--p-primary-contrast-color);
}

.popup-pager-count {
    font-size: 1.15rem;
    font-weight: 600;
}

.popup-pager-actions {
    display: flex;
    align-items: center;
    gap: 0.65rem;
}

.popup-pager-button {
    --p-button-primary-background: var(--p-primary-hover-color);
    --p-button-primary-border-color: var(--p-primary-hover-color);
    --p-button-primary-hover-background: var(--p-primary-active-color);
    --p-button-primary-hover-border-color: var(--p-primary-active-color);
    width: 2.4rem;
    height: 2.4rem;
    padding: 0;
}

.popup-content {
    display: flex;
    flex: 1;
    flex-direction: column;
    min-height: 0;
    overflow-y: auto;
    transition: opacity var(--p-transition-duration);
}

.popup-content-stale {
    opacity: 0.5;
}

.popup-header {
    display: flex;
    flex-direction: column;
    gap: 0.55rem;
    padding-block: 1.1rem 0.8rem;
    padding-inline: 1.45rem;
}

.popup-title {
    color: var(--p-primary-color);
    font-size: 1.6rem;
    font-weight: 700;
    line-height: 1.25;
}

.popup-badges {
    --popup-badge-font-size: 1.1rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.55rem;
}

.popup-model-badge,
.popup-status-badge {
    --p-tag-icon-size: var(--popup-badge-font-size);
    font-size: var(--popup-badge-font-size);
    text-transform: uppercase;
}

.popup-body {
    display: flex;
    flex-direction: column;
    gap: 0.65rem;
    padding-block: 0.65rem 0.95rem;
    padding-inline: 1.45rem;
}

.popup-html-content {
    overflow-wrap: break-word;
}

.popup-snippet-section {
    padding-block-end: 1.1rem;
    padding-inline: 1.45rem;
}

.popup-snippet {
    margin: 0;
    padding-block-start: 0.95rem;
    border-block-start: 0.1rem dashed var(--p-content-border-color);
    color: var(--p-text-muted-color);
    font-size: 1.3rem;
    line-height: 1.4;
}

.popup-footer {
    display: flex;
    align-items: center;
    padding-block: 0.6rem;
    padding-inline: 1.2rem;
    border-block-start: 0.1rem solid var(--p-content-border-color);
    background: var(--p-content-hover-background);
}

.popup-footer-link {
    padding-inline: 0.25rem;
    font-size: 1.25rem;
    font-weight: 600;
}
</style>
