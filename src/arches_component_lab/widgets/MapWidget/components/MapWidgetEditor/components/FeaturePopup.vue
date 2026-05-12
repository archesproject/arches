<script setup lang="ts">
import { computed, ref, watch } from "vue";

import arches from "arches";
import Button from "primevue/button";
import Skeleton from "primevue/skeleton";
import { useGettext } from "vue3-gettext";

import { fetchResourceDescriptor } from "@/arches_component_lab/widgets/MapWidget/api.ts";

import type { MapGeoJSONFeature } from "maplibre-gl";

import type { ResourceDescriptor } from "@/arches_component_lab/widgets/MapWidget/types.ts";

const { features } = defineProps<{ features: MapGeoJSONFeature[] }>();

const { $gettext } = useGettext();

const index = ref(0);
const isLoading = ref(false);
const descriptor = ref<ResourceDescriptor | null>(null);

const feature = computed(() => features[index.value]);
const resourceId = computed(
    () => feature.value?.properties?.resourceinstanceid ?? null,
);
const total = computed(() => features.length);

watch(
    resourceId,
    async (id) => {
        descriptor.value = null;
        if (!id) return;
        isLoading.value = true;
        try {
            descriptor.value = await fetchResourceDescriptor(id);
        } catch (error) {
            console.error("Error fetching resource descriptor:", error);
        } finally {
            isLoading.value = false;
        }
    },
    { immediate: true },
);

function navigateToPreviousFeature() {
    index.value = (index.value - 1 + total.value) % total.value;
}

function navigateToNextFeature() {
    index.value = (index.value + 1) % total.value;
}
</script>

<template>
    <div class="popup">
        <div class="popup-title-bar">
            <Button
                v-if="total > 1"
                icon="pi pi-chevron-left"
                severity="secondary"
                text
                rounded
                @click="navigateToPreviousFeature"
            />
            <div class="popup-title">
                <Skeleton
                    v-if="isLoading"
                    height="1rem"
                    width="60%"
                />
                <template v-else>
                    {{ descriptor?.displayname ?? resourceId }}
                </template>
            </div>
            <Button
                v-if="total > 1"
                icon="pi pi-chevron-right"
                severity="secondary"
                text
                rounded
                @click="navigateToNextFeature"
            />
        </div>

        <div class="popup-body">
            <template v-if="isLoading">
                <Skeleton
                    height="1rem"
                    class="popup-skeleton-row"
                />
                <Skeleton
                    height="1rem"
                    width="80%"
                    class="popup-skeleton-row"
                />
                <Skeleton
                    height="1rem"
                    width="60%"
                    class="popup-skeleton-row"
                />
            </template>
            <template v-else-if="descriptor">
                <!-- eslint-disable-next-line vue/no-v-html -->
                <div
                    v-if="descriptor.map_popup"
                    class="popup-html-content"
                    v-html="descriptor.map_popup"
                />
                <div class="popup-metadata-block">
                    <div
                        v-if="descriptor.graph_name"
                        class="popup-metadata"
                    >
                        {{
                            $gettext("Resource Model: %{name}", {
                                name: descriptor.graph_name,
                            })
                        }}
                    </div>
                    <div
                        v-if="resourceId"
                        class="popup-metadata popup-id-value"
                    >
                        {{ $gettext("ID: %{id}", { id: resourceId }) }}
                    </div>
                </div>
            </template>
        </div>

        <div class="popup-footer">
            <Button
                v-if="resourceId"
                as="a"
                :href="arches.urls.resource_report + resourceId"
                target="_blank"
                icon="pi pi-book"
                :label="$gettext('Report')"
                severity="secondary"
                text
                size="small"
            />
            <div
                v-if="total > 1"
                class="popup-counter"
            >
                {{
                    $gettext("%{current} of %{total}", {
                        current: String(index + 1),
                        total: String(total),
                    })
                }}
            </div>
        </div>
    </div>
</template>

<style scoped>
.popup {
    display: flex;
    flex-direction: column;
    height: 100%;
    font-size: 1.375rem;
    border: 0.0625rem solid var(--p-menubar-border-color);
    border-radius: 0.25rem;
    overflow: hidden;
    background: var(--p-content-background);
    color: var(--p-content-color);
}

.popup-title-bar {
    display: flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.5rem 3.5rem 0.5rem 0.625rem;
    border-bottom: 0.0625rem solid var(--p-menubar-border-color);
    min-height: 2.5rem;
}

.popup-title {
    flex: 1;
    min-width: 0;
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.popup-body {
    flex: 1;
    padding: 0.75rem 1rem;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.popup-skeleton-row {
    display: block;
}

.popup-html-content {
    margin-bottom: 0.5rem;
}

.popup-metadata-block {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    font-size: 1.125rem;
    opacity: 0.75;
}

.popup-metadata {
    display: flex;
    gap: 0.25rem;
}

.popup-metadata-value {
    color: var(--p-primary-color);
}

.popup-id-value {
    word-break: break-all;
}

.popup-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.5rem 1rem;
    border-top: 0.0625rem solid var(--p-menubar-border-color);
    background: var(--p-button-secondary-hover-background);
}

.popup-counter {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    font-weight: 500;
    font-size: 1rem;
}
</style>
