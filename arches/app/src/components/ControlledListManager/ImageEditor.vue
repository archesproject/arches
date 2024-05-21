<script setup lang="ts">
import arches from "arches";
import { computed, inject } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import { useToast } from "primevue/usetoast";

import AddMetadata from "@/components/ControlledListManager/AddMetadata.vue";
import ImageMetadata from "@/components/ControlledListManager/ImageMetadata.vue";

import { DANGER, METADATA_CHOICES, itemKey } from "@/components/ControlledListManager/constants.ts";
import { deleteImage } from "@/components/ControlledListManager/api.ts";
import { bestLabel } from "@/components/ControlledListManager/utils.ts";

import type { Ref } from "vue";
import type {
    ControlledListItem,
    ControlledListItemImage,
} from "@/types/ControlledListManager";

const item = inject(itemKey) as Ref<ControlledListItem>;
const { image } = defineProps<{ image: ControlledListItemImage }>();

const toast = useToast();
const { $gettext } = useGettext();

const labeledMetadataChoices = [
    {
        type: METADATA_CHOICES.title,
        label: $gettext('Title'),
    },
    {
        type: METADATA_CHOICES.alternativeText,
        label: $gettext('Alternative text'),
    },
    {
        type: METADATA_CHOICES.description,
        label: $gettext('Description'),
    },
    {
        type: METADATA_CHOICES.attribution,
        label: $gettext('Attribution'),
    },
];

const bestTitle = computed(() => {
    return image.metadata.filter(metadatum => metadatum.metadata_type === METADATA_CHOICES.title)
        .find(title => title.language_id === arches.activeLanguage)?.value;
});

const bestAlternativeText = computed(() => {
    return image.metadata.filter(metadatum => metadatum.metadata_type === METADATA_CHOICES.alternativeText)
        .find(altText => altText.language_id === arches.activeLanguage)?.value
        || bestLabel(item.value, arches.activeLanguage).value;
});

const onDeleteImage = async () => {
    const deleted = await deleteImage(image, toast, $gettext);
    if (deleted) {
        removeImage(image);
    }
};

const removeImage = (removedImage: ControlledListItemImage) => {
    const toDelete = item.value!.images.findIndex(
        (imageFromItem) => imageFromItem.id === removedImage.id
    );
    item.value!.images.splice(toDelete, 1);
};
</script>

<template>
    <div>
        <img
            :src="image.url"
            :title="bestTitle"
            :alt="bestAlternativeText"
            width="200"
        >
        <div>
            <ImageMetadata
                :metadata="image.metadata"
                :labeled-metadata-choices
            />
            <div style="display: flex; gap: 1rem;">
                <AddMetadata
                    :image
                    :labeled-metadata-choices
                />
                <Button
                    raised
                    :severity="DANGER"
                    icon="fa fa-trash"
                    :label="$gettext('Delete image')"
                    @click="onDeleteImage"
                />
            </div>
        </div>
    </div>
</template>

<style scoped>
.p-button {
    height: 3rem;
    margin-top: 1rem;
}
:deep(.p-button-icon),
:deep(.p-button-label) {
    color: white;
    font-size: small;
    font-weight: 600;
}
</style>
