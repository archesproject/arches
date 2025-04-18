<script setup lang="ts">
import arches from "arches";
import { computed, inject } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";

import {
    isEditingKey,
    itemKey,
    CONTRAST,
    PRIMARY,
} from "@/arches_controlled_lists/constants.ts";
import {
    dataIsNew,
    shouldUseContrast,
} from "@/arches_controlled_lists/utils.ts";

import type { Ref } from "vue";
import type {
    ControlledListItem,
    ControlledListItemImage,
    ControlledListItemImageMetadata,
    IsEditingRefAndSetter,
    LabeledChoice,
} from "@/arches_controlled_lists/types";

const { labeledChoices, image, makeMetadataEditable } = defineProps<{
    labeledChoices: LabeledChoice[];
    image: ControlledListItemImage;
    makeMetadataEditable: (
        clickedMetadata: ControlledListItemImageMetadata,
        index: number,
    ) => void;
}>();
const item = inject(itemKey) as Ref<ControlledListItem>;
const { isEditing } = inject(isEditingKey) as IsEditingRefAndSetter;

const { $gettext } = useGettext();

const newMetadata: Ref<ControlledListItemImageMetadata> = computed(() => {
    const otherNewMetadataIds = image.metadata
        .filter((metadatum) => dataIsNew(metadatum))
        .map((metadatum) => Number.parseInt(metadatum.id));

    const maxOtherNewMetadataId = Math.max(...otherNewMetadataIds, 0);

    const nextMetadataType =
        labeledChoices.find(
            (choice) =>
                !image.metadata
                    .map((metadatum) => metadatum.metadata_type)
                    .includes(choice.type),
        ) ?? labeledChoices[0];

    return {
        id: (maxOtherNewMetadataId + 1).toString(),
        metadata_type: nextMetadataType.type,
        metadata_label: nextMetadataType.label,
        language_id: arches.activeLanguage,
        list_item_image_id: image.id,
        value: "",
    };
});

const addMetadata = () => {
    const staticNewMetadata = newMetadata.value;
    item.value.images
        .find((imageFromItem) => imageFromItem.id === image.id)!
        .metadata.push(staticNewMetadata);
    makeMetadataEditable(staticNewMetadata, -1);
};
</script>

<template>
    <Button
        class="add-metadata"
        icon="fa fa-plus-circle"
        :severity="shouldUseContrast() ? CONTRAST : PRIMARY"
        :label="$gettext('Metadata')"
        :disabled="isEditing"
        @click="addMetadata"
    />
</template>

<style scoped>
.add-metadata {
    display: flex;
    height: 3rem;
    margin-top: 1rem;
}
</style>
