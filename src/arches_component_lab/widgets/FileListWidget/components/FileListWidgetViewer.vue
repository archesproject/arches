<script setup lang="ts">
import { computed, onMounted } from "vue";

import arches from "arches";
import { Image, Galleria } from "primevue";

import type {
    FileListAliasedNodeData,
    FileReference,
} from "@/arches_component_lab/datatypes/file-list/types";

const { aliasedNodeData } = defineProps<{
    aliasedNodeData: FileListAliasedNodeData;
}>();

const emit = defineEmits<{
    initialized: [updatedValue: FileListAliasedNodeData];
}>();

onMounted(() => {
    emit("initialized", aliasedNodeData);
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
        originalUrl.startsWith(arches.urls.url_subpath)
    ) {
        return originalUrl;
    }
    return (arches.urls.url_subpath + originalUrl).replace("//", "/");
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
