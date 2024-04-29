<script setup lang="ts">
import arches from "arches";
import { computed, inject } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";

import { itemKey } from "@/components/ControlledListManager/const.ts";

import type {
    ControlledListItemImage,
    ControlledListItemImageMetadata,
    MetadataChoice,
    NewControlledListItemImageMetadata,
} from "@/types/ControlledListManager";

const { choices: METADATA_CHOICES, image } : {
    choices: MetadataChoice[], image: ControlledListItemImage
} = defineProps(["choices", "image"]);
const { item } = inject(itemKey);

const { $gettext } = useGettext();
const slateBlue = "#2d3c4b"; // todo: import from theme somewhere

const newMetadata: NewControlledListItemImageMetadata = computed(() => {
    const otherNewMetadatas = image.metadata.filter(
        (m: NewControlledListItemImageMetadata | ControlledListItemImageMetadata) => typeof m.id === "number"
    // eslint-disable-next-line @typescript-eslint/no-explicit-any 
    ) as any as NewControlledListItemImageMetadata[];
    const maxOtherNewMetadataId = Math.max(
        ...otherNewMetadatas.map(m => m.id),
        1000,
    );

    const nextMetadataType = METADATA_CHOICES.find(
        choice => !image.metadata.map(
            (m: ControlledListItemImageMetadata | NewControlledListItemImageMetadata) => m.metadata_type
        ).includes(choice.type)
    ) ?? METADATA_CHOICES[0];

    return {
        id: maxOtherNewMetadataId + 1,
        metadata_type: nextMetadataType.type,
        metadata_label: nextMetadataType.label,
        language_id: arches.activeLanguage,
        controlled_list_item_image_id: image.id,
        value: '',
    };
});
</script>

<template>
    <Button
        class="add-metadata"
        raised
        @click="item.images.find(i => i.id === image.id).metadata.push(newMetadata)"
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
    color: v-bind(slateBlue);
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
