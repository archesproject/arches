<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { Image, Galleria } from "openvue";

import { useLanguageStore } from "@/arches_vue_components/stores/useLanguageStore.ts";
import { useSettingsStore } from "@/arches_vue_components/stores/useSettingsStore.ts";

import type {
    FileListAliasedNodeData,
    FileReference,
} from "@/arches_vue_components/datatypes/file-list/types";

const { aliasedNodeData } = defineProps<{
    aliasedNodeData: FileListAliasedNodeData;
}>();

const languageStore = useLanguageStore();
const settingsStore = useSettingsStore();
const forceScriptName = ref("");

onMounted(async () => {
    forceScriptName.value = await settingsStore.fetchForceScriptName();
    await languageStore.fetchAllLanguages();
});

const fileReferences = computed(() => aliasedNodeData?.node_value ?? []);

const imageData = computed(() => {
    return fileReferences.value
        .filter(isImage)
        .map((fileReference: FileReference) => {
            return {
                thumbnailImageSrc: getFileUrl(fileReference.url),
                itemImageSrc: getFileUrl(fileReference.url),
                alt: altText(fileReference),
            };
        });
});

// Files a browser can't show as an image (PDFs, spreadsheets, ...) are listed
// as links instead of being handed to the gallery as broken images.
const otherFiles = computed(() => {
    return fileReferences.value
        .filter((fileReference) => !isImage(fileReference))
        .map((fileReference) => {
            return {
                name: fileReference.name || fileReference.url,
                url: getFileUrl(fileReference.url),
                icon: fileIcon(fileReference),
            };
        });
});

const showThumbnails = computed(() => {
    return imageData.value.length > 1;
});

// Uploads can arrive with a blank MIME type, so fall back to the extension.
function fileExtension(fileReference: FileReference): string {
    const fileName = fileReference.name || fileReference.url || "";
    return fileName.split(".").pop()?.toLowerCase() ?? "";
}

function isImage(fileReference: FileReference): boolean {
    if (fileReference.type) {
        return fileReference.type.startsWith("image/");
    }
    return /^(jpe?g|png|gif|webp|bmp|svg|tiff?)$/.test(
        fileExtension(fileReference),
    );
}

function fileIcon(fileReference: FileReference): string {
    const mimeType = fileReference.type ?? "";
    const extension = fileExtension(fileReference);
    if (mimeType === "application/pdf" || extension === "pdf") {
        return "pi pi-file-pdf";
    }
    if (
        /msword|wordprocessingml|opendocument\.text/.test(mimeType) ||
        /^(docx?|odt|rtf)$/.test(extension)
    ) {
        return "pi pi-file-word";
    }
    if (
        /ms-excel|spreadsheetml|opendocument\.spreadsheet|text\/csv/.test(
            mimeType,
        ) ||
        /^(xlsx?|ods|csv)$/.test(extension)
    ) {
        return "pi pi-file-excel";
    }
    return "pi pi-file";
}

function getFileUrl(originalUrl: string) {
    const httpRegex = /^(blob:|https?:\/\/)/;
    if (
        !originalUrl ||
        httpRegex.test(originalUrl) ||
        originalUrl.startsWith(forceScriptName.value)
    ) {
        return originalUrl;
    }
    return (forceScriptName.value + originalUrl).replace("//", "/");
}

function altText(fileReference: FileReference): string {
    const languageCode = languageStore.requestLanguageCode;
    if (languageCode === null) {
        return "";
    }
    return fileReference.altText?.[languageCode]?.value ?? "";
}
</script>

<template>
    <Galleria
        v-if="imageData.length > 0"
        :value="imageData"
        :show-thumbnails="showThumbnails"
    >
        <template #item="slotProps">
            <Image
                class="mainImage"
                :src="slotProps.item.itemImageSrc"
                :alt="slotProps.item.alt"
            />
        </template>
        <template
            v-if="showThumbnails"
            #thumbnail="slotProps"
        >
            <Image
                class="thumbnailImage"
                :src="slotProps.item.itemImageSrc"
                :alt="slotProps.item.alt"
            />
        </template>
    </Galleria>
    <ul
        v-if="otherFiles.length > 0"
        class="file-list-viewer-files"
    >
        <li
            v-for="(file, fileIndex) in otherFiles"
            :key="fileIndex"
        >
            <a
                class="file-list-viewer-file"
                :href="file.url"
                :title="file.name"
                target="_blank"
                rel="noopener"
            >
                <i
                    :class="file.icon"
                    aria-hidden="true"
                />
                <span class="file-list-viewer-file-name">{{ file.name }}</span>
            </a>
        </li>
    </ul>
</template>

<style scoped>
.file-list-viewer-files {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    margin: 0;
    padding: 0;
    list-style: none;
}

.file-list-viewer-file {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    max-inline-size: 100%;
    color: var(--p-primary-color);
    text-decoration: none;
}

.file-list-viewer-file:hover {
    text-decoration: underline;
}

.file-list-viewer-file-name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

:deep(.mainImage) {
    display: flex;
    justify-content: center;
    align-items: center;
}

:deep(.mainImage img) {
    max-width: 100%;
}

:deep(.thumbnailImage img) {
    max-height: 5rem;
}

:deep(.p-galleria-thumbnail-item) {
    overflow: hidden;
    cursor: pointer;
}
</style>
