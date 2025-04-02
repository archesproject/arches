<script setup lang="ts">
import arches from "arches";
import { computed, inject, useTemplateRef } from "vue";

import { getItemLabel } from "@/arches_vue_utils/utils.ts";
import {
    itemKey,
    METADATA_CHOICES,
    systemLanguageKey,
} from "@/arches_controlled_lists/constants.ts";
import ImageMetadata from "@/arches_controlled_lists/components/editor/ImageMetadata.vue";

import type { Ref } from "vue";
import type { Language } from "@/arches_vue_utils/types";
import type {
    ControlledListItem,
    ControlledListItemImage,
} from "@/arches_controlled_lists/types";

const metadataEditor = useTemplateRef("metadataEditor");

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

defineExpose({ isEditing: metadataEditor.value?.isEditing });
</script>

<template>
    <div>
        <img
            :src="image.url"
            :title="bestTitle"
            :alt="bestAlternativeText"
            width="200"
        />
        <ImageMetadata
            ref="metadataEditor"
            :image="image"
        />
    </div>
</template>
