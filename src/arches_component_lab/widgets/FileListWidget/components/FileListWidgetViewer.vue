<script setup lang="ts">
import { computed } from "vue";
import { Image, Galleria } from "primevue";
import type { FileReference } from "@/arches_component_lab/widgets/types.ts";

const props = defineProps<{
    value: FileReference[] | null | undefined;
}>();

const imageData = computed(() => {
    return props.value?.map((fileReference) => {
        return {
            thumbnailImageSrc: `${fileReference.url}`,
            itemImageSrc: `${fileReference.url}`,
            alt: fileReference.altText,
            title: fileReference.title,
        };
    });
});

const showThumbnails = computed(() => {
    return imageData.value && imageData.value.length > 1;
});
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
</style>
