<script setup lang="ts">
import arches from "arches";
import { computed, inject } from "vue";

import { itemKey, METADATA_CHOICES } from "@/controlledlists/constants.ts";
import { bestLabel } from "@/controlledlists/utils.ts";
import ImageMetadata from "@/controlledlists/components/editor/ImageMetadata.vue";

import type { Ref } from "vue";
import type {
    ControlledListItem,
    ControlledListItemImage,
} from "@/controlledlists/types";

const item = inject(itemKey) as Ref<ControlledListItem>;
const { image } = defineProps<{ image: ControlledListItemImage }>();

const bestTitle = computed(() => {
    const titles = image.metadata.filter(
        (metadatum) => metadatum.metadata_type === METADATA_CHOICES.title,
    );
    return (
        titles.find((title) => title.language_id === arches.activeLanguage)
            ?.value || titles[0]?.value
    );
});

const bestAlternativeText = computed(() => {
    return (
        image.metadata
            .filter(
                (metadatum) =>
                    metadatum.metadata_type ===
                    METADATA_CHOICES.alternativeText,
            )
            .find((altText) => altText.language_id === arches.activeLanguage)
            ?.value || bestLabel(item.value, arches.activeLanguage).value
    );
});
</script>

<template>
    <div>
        <img
            :src="image.url"
            :title="bestTitle"
            :alt="bestAlternativeText"
            width="200"
        />
        <ImageMetadata :image="image" />
    </div>
</template>
