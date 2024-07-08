<script setup lang="ts">
import arches from "arches";
import { computed, inject } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";

import { ARCHES_CHROME_BLUE } from "@/arches/theme.ts";
import { itemKey } from "@/controlledlists/constants.ts";

import type { Ref } from "vue";
import type {
    ControlledListItem,
    ControlledListItemImage,
    LabeledChoice,
    NewControlledListItemImageMetadata,
} from "@/controlledlists/types";

const { labeledChoices, image, makeMetadataEditable } = defineProps<{
    labeledChoices: LabeledChoice[];
    image: ControlledListItemImage;
    makeMetadataEditable: (
        clickedMetadata: NewControlledListItemImageMetadata,
        index: number,
    ) => void;
}>();
const item = inject(itemKey) as Ref<ControlledListItem>;

const { $gettext } = useGettext();

const newMetadata: Ref<NewControlledListItemImageMetadata> = computed(() => {
    const otherNewMetadataIds = image.metadata
        .filter((metadatum) => typeof metadatum.id === "number")
        .map((metadatum) => metadatum.id as number);

    const maxOtherNewMetadataId = Math.max(...otherNewMetadataIds, 0);

    const nextMetadataType =
        labeledChoices.find(
            (choice) =>
                !image.metadata
                    .map((metadatum) => metadatum.metadata_type)
                    .includes(choice.type),
        ) ?? labeledChoices[0];

    return {
        id: maxOtherNewMetadataId + 1,
        metadata_type: nextMetadataType.type,
        metadata_label: nextMetadataType.label,
        language_id: arches.activeLanguage,
        controlled_list_item_image_id: image.id,
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
        raised
        @click="addMetadata"
    >
        <i
            class="fa fa-plus-circle"
            aria-hidden="true"
        />
        <span class="add-metadata-text">
            {{ $gettext("Add metadata") }}
        </span>
    </Button>
</template>

<style scoped>
.add-metadata {
    display: flex;
    height: 3rem;
    color: v-bind(ARCHES_CHROME_BLUE);
    background-color: #f3fbfd;
    margin-top: 1rem;
}
.add-metadata > i,
.add-metadata > span {
    align-self: center;
    font-size: small;
}
.add-metadata-text {
    margin: 1rem;
    font-size: small;
    font-weight: 600;
}
</style>
