<script setup lang="ts">
import { ref, useTemplateRef } from "vue";

import { useGettext } from "vue3-gettext";

import shp from "shpjs";

import FileUpload from "primevue/fileupload";
import Message from "primevue/message";
import ProgressSpinner from "primevue/progressspinner";

import { useResolvedMapContext } from "@/arches_vue_components/components/MapComponent/composables/useMapContext.ts";

import type { FeatureCollection } from "geojson";
import type { MapContext } from "@/arches_vue_components/components/MapComponent/types.ts";

const ACCEPTED_EXTENSIONS = ["zip", "shp"];

const { context = undefined } = defineProps<{
    context?: MapContext;
}>();

const { addFeatures } = useResolvedMapContext(context, "ShapefileDropZone");

const { $gettext } = useGettext();

const isLoading = ref(false);
const errorMessage = ref<string | null>(null);

const fileUploadRef =
    useTemplateRef<InstanceType<typeof FileUpload>>("fileUpload");

async function onSelect(event: { files: File[] }): Promise<void> {
    const file = event.files[0];
    if (!file) return;

    errorMessage.value = null;

    const extension = file.name.split(".").pop()?.toLowerCase();
    if (!extension || !ACCEPTED_EXTENSIONS.includes(extension)) {
        errorMessage.value = $gettext(
            "Unsupported file type. Drop a zipped shapefile (.zip) or a .shp file.",
        );
        return;
    }

    isLoading.value = true;

    try {
        const buffer = await file.arrayBuffer();
        const parsed =
            extension === "shp"
                ? await shp({ shp: buffer })
                : await shp(buffer);

        const collections: FeatureCollection[] = Array.isArray(parsed)
            ? parsed
            : [parsed];
        const features = collections.flatMap(
            (collection) => collection.features,
        );

        if (!features.length) {
            errorMessage.value = $gettext("No features found in that file.");
            return;
        }

        addFeatures(features);
    } catch {
        errorMessage.value = $gettext("Unable to parse that shapefile.");
    } finally {
        isLoading.value = false;
    }
}

function openFileChooser(): void {
    // @ts-expect-error FileUpload does not have a type definition for $el
    const rootElement = fileUploadRef.value?.$el;
    rootElement?.querySelector('input[type="file"]')?.click();
}
</script>

<template>
    <div class="shapefile-drop-zone">
        <FileUpload
            ref="fileUpload"
            accept=".zip,.shp"
            :multiple="false"
            :show-cancel-button="false"
            :show-upload-button="false"
            :custom-upload="true"
            @select="onSelect($event)"
        >
            <template #content>
                <div
                    class="drop-zone-content"
                    @click="openFileChooser"
                >
                    <ProgressSpinner
                        v-if="isLoading"
                        style="width: 2rem; height: 2rem"
                        stroke-width="6"
                    />
                    <i
                        v-else
                        class="pi pi-map-marker drop-zone-icon"
                        aria-hidden="true"
                    />
                    <div class="drop-zone-title">
                        {{
                            isLoading
                                ? $gettext("Parsing shapefile…")
                                : $gettext("Drop a shapefile here")
                        }}
                    </div>
                    <div class="drop-zone-subtitle">
                        {{ $gettext("or click to browse (.zip or .shp)") }}
                    </div>
                </div>
            </template>
        </FileUpload>
        <Message
            v-if="errorMessage"
            severity="error"
            size="small"
        >
            {{ errorMessage }}
        </Message>
    </div>
</template>

<style scoped>
.shapefile-drop-zone {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

:deep(.p-fileupload-header) {
    display: none;
}

:deep(.p-fileupload-content) {
    padding: 0;
}

.drop-zone-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 1rem;
    cursor: pointer;
}

.drop-zone-icon {
    font-size: 1.75rem;
    color: var(--p-primary-color);
}

.drop-zone-title {
    font-weight: bold;
    color: var(--p-text-color);
}

.drop-zone-subtitle {
    font-size: 0.875rem;
    color: var(--p-text-muted-color);
}
</style>
