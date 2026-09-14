<script setup lang="ts">
import arches from "arches";
import { computed, inject } from "vue";

import {
    itemKey,
    METADATA_CHOICES,
    systemLanguageKey,
} from "@/arches_controlled_lists/constants.ts";
import { getItemLabel } from "@/arches_controlled_lists/utils.ts";
import ImageMetadata from "@/arches_controlled_lists/components/editor/ImageMetadata.vue";

import type { Ref } from "vue";
import type {
    ControlledListItem,
    ControlledListItemImage,
    Language,
} from "@/arches_controlled_lists/types";

const item = inject(itemKey) as Ref<ControlledListItem>;
const systemLanguage = inject(systemLanguageKey) as Language;

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
            ?.value ||
        getItemLabel(item.value, arches.activeLanguage, systemLanguage.code)
            .value
    );
});
</script>

<template>
    <div>
        <img
            :src="image.url"
            :title="bestTitle"
            :alt="bestAlternativeText"
            width="400"
        />
        <ImageMetadata :image="image" />
    </div>
</template>
