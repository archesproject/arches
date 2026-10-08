<script setup lang="ts">
import { ref, useTemplateRef } from "vue";

import { useGettext } from "vue3-gettext";

import Button from "openvue/button";
import FileUpload from "openvue/fileupload";
import Message from "openvue/message";
import ProgressSpinner from "openvue/progressspinner";

import {
    ACCEPTED_GEOMETRY_FILE_EXTENSIONS,
    GeometryImportError,
    parseGeometryFile,
} from "@/arches_vue_components/components/MapComponent/utils/geometry-import.ts";

import { useResolvedMapContext } from "@/arches_vue_components/components/MapComponent/composables/useMapContext.ts";

import type { MapContext } from "@/arches_vue_components/components/MapComponent/types.ts";
import type { GeometryImportErrorCode } from "@/arches_vue_components/components/MapComponent/utils/geometry-import.ts";

const ACCEPTED_FILE_TYPES = ACCEPTED_GEOMETRY_FILE_EXTENSIONS.map(
    (extension) => `.${extension}`,
).join(",");

const { context = undefined } = defineProps<{
    context?: MapContext;
}>();

const fileUpload =
    useTemplateRef<InstanceType<typeof FileUpload>>("fileUpload");

const { addFeatures } = useResolvedMapContext(context, "FileDropZone");

const { $gettext } = useGettext();

const isLoading = ref(false);
const errorMessage = ref<string | null>(null);

function getErrorMessage(code: GeometryImportErrorCode): string {
    if (code === "unsupported-file-type") {
        return $gettext(
            "Unsupported file type. Use a zipped shapefile (.zip), .shp, GeoJSON (.json, .geojson), or KML (.kml) file.",
        );
    }
    if (code === "no-features") {
        return $gettext("No features found in that file.");
    }
    return $gettext("Unable to read that file.");
}

async function onSelect(event: { files: File[] }): Promise<void> {
    const file = event.files[0];
    if (!file) {
        return;
    }

    errorMessage.value = null;
    isLoading.value = true;

    try {
        addFeatures(await parseGeometryFile(file));
    } catch (error) {
        if (error instanceof GeometryImportError) {
            errorMessage.value = getErrorMessage(error.code);
        } else {
            errorMessage.value = getErrorMessage("parse-failed");
        }
    } finally {
        isLoading.value = false;
        // @ts-expect-error FileUpload does not have a type definition for clear
        fileUpload.value?.clear();
    }
}

function openFileChooser(): void {
    // @ts-expect-error FileUpload does not have a type definition for $el
    const rootElement = fileUpload.value?.$el;
    rootElement?.querySelector('input[type="file"]')?.click();
}
</script>

<template>
    <div class="file-drop-zone">
        <FileUpload
            ref="fileUpload"
            :accept="ACCEPTED_FILE_TYPES"
            :multiple="false"
            :show-cancel-button="false"
            :show-upload-button="false"
            :custom-upload="true"
            @select="onSelect($event)"
        >
            <template #content>
                <div class="drop-zone-content">
                    <ProgressSpinner
                        v-if="isLoading"
                        class="drop-zone-spinner"
                        stroke-width="6"
                    />
                    <i
                        v-else
                        class="pi pi-upload drop-zone-icon"
                        aria-hidden="true"
                    />
                    <span class="drop-zone-text">
                        {{
                            $gettext(
                                "Drag and drop a shapefile, GeoJSON, or KML file here to add its geometry.",
                            )
                        }}
                    </span>
                    <Button
                        class="drop-zone-upload-button"
                        size="small"
                        :label="$gettext('Upload file')"
                        :link="true"
                        @click="openFileChooser"
                    />
                </div>
            </template>
        </FileUpload>
        <Message
            v-if="errorMessage"
            severity="error"
            size="small"
            role="alert"
        >
            {{ errorMessage }}
        </Message>
    </div>
</template>

<style scoped>
.file-drop-zone {
    display: flex;
    flex-direction: column;
    gap: 0.65rem;
}

.file-drop-zone :deep(.p-fileupload) {
    border: 0.2rem dashed var(--p-primary-color);
    border-radius: 0.65rem;
    background: var(--p-content-hover-background);
}

.file-drop-zone :deep(.p-fileupload-header) {
    display: none;
}

.file-drop-zone :deep(.p-fileupload-content) {
    padding: 0;
    border: none;
}

.file-drop-zone :deep(.p-fileupload-content[data-p-highlight="true"]) {
    background: var(--p-highlight-background);
}

.drop-zone-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.55rem;
    padding-block: 1.2rem;
    padding-inline: 1rem;
    text-align: center;
}

.drop-zone-icon {
    color: var(--p-primary-color);
    font-size: 2.1rem;
}

.drop-zone-spinner {
    width: 2.1rem;
    height: 2.1rem;
}

.drop-zone-text {
    color: var(--p-text-muted-color);
    font-size: 1.15rem;
    line-height: 1.5;
}

.drop-zone-upload-button {
    padding: 0;
    font-size: 1.15rem;
    font-weight: 600;
}
</style>
