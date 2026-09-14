<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { Image, Galleria } from "primevue";

import { useSettingsStore } from "@/arches_vue_components/stores/useSettingsStore.ts";

import type {
    FileListAliasedNodeData,
    FileReference,
} from "@/arches_vue_components/datatypes/file-list/types";

const { aliasedNodeData } = defineProps<{
    aliasedNodeData: FileListAliasedNodeData;
}>();

const settingsStore = useSettingsStore();
const forceScriptName = ref("");

onMounted(async () => {
    forceScriptName.value = await settingsStore.fetchForceScriptName();
});

const imageData = computed(() => {
    return aliasedNodeData?.node_value?.map((fileReference: FileReference) => {
        return {
            thumbnailImageSrc: getFileUrl(fileReference.url),
            itemImageSrc: getFileUrl(fileReference.url),
            alt: fileReference.altText,
            title: fileReference.title,
        };
    });
});

const showThumbnails = computed(() => {
    return imageData.value && imageData.value.length > 1;
});

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
</script>

<template>
    <Galleria
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
</template>

<style scoped>
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
