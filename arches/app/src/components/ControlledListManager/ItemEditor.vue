<script setup lang="ts">
import arches from "arches";
import Cookies from "js-cookie";
import { computed, inject, provide } from "vue";
import { useGettext } from "vue3-gettext";

import FileUpload from "primevue/fileupload";

import ImageEditor from "@/components/ControlledListManager/ImageEditor.vue";
import ItemCharacteristic from "@/components/ControlledListManager/ItemCharacteristic.vue";
import LabelEditor from "@/components/ControlledListManager/LabelEditor.vue";
import LetterCircle from "@/components/ControlledListManager/LetterCircle.vue";

import {
    displayedRowKey,
    itemKey,
    selectedLanguageKey,
    ALT_LABEL,
    PREF_LABEL,
} from "@/components/ControlledListManager/const.ts";
import { bestLabel } from "@/components/ControlledListManager/utils.ts";

import type { FileUploadBeforeSendEvent, FileUploadUploadEvent } from "primevue/fileupload";
import type {
    ControlledListItem,
    ControlledListItemImage,
    ControlledListItemImageMetadata,
    Label,
    NewControlledListItemImageMetadata,
    NewLabel,
} from "@/types/ControlledListManager";

const { displayedRow: item } = inject(displayedRowKey);
const selectedLanguage = inject(selectedLanguageKey);

const { $gettext } = useGettext();
const slateBlue = "#2d3c4b"; // todo: import from theme somewhere

provide(itemKey, { item });

const appendItemLabel = computed(() => {
    return (newLabel: Label | NewLabel) => { item.value.labels.push(newLabel); };
});
const removeItemLabel = computed(() => {
    return (removedLabel: Label | NewLabel) => {
        const toDelete = item.value.labels.findIndex((l: Label | NewLabel) => l.id === removedLabel.id);
        item.value.labels.splice(toDelete, 1);
    };
});
const updateItemLabel = computed(() => {
    return (updatedLabel: Label) => {
        const toUpdate = item.value.labels.find((l: Label) => l.id === updatedLabel.id);
        toUpdate.language_id = updatedLabel.language_id;
        toUpdate.value = updatedLabel.value;
    };
});

const appendImageMetadata = computed(() => {
    return (newMetadata: ControlledListItemImageMetadata | NewControlledListItemImageMetadata) => {
        item.value.images.find(
            (i: ControlledListItemImage) => i.id === newMetadata.controlled_list_item_image_id
        ).metadata.push(newMetadata);
    };
});
const removeImageMetadata = computed(() => {
    return (removedMetadata: ControlledListItemImageMetadata | NewControlledListItemImageMetadata) => {
        const imageFromItem = item.value.images.find(
            (i: ControlledListItemImage) => i.id === removedMetadata.controlled_list_item_image_id
        );
        const toDelete = imageFromItem.metadata.findIndex(
            (m: ControlledListItemImageMetadata | NewControlledListItemImageMetadata) => m.id === removedMetadata.id
        );
        imageFromItem.metadata.splice(toDelete, 1);
    };
});
const updateImageMetadata = computed(() => {
    return (updatedMetadata: ControlledListItemImageMetadata) => {
        const imageFromItem = item.value.images.find(
            (i: ControlledListItemImage) => i.id === updatedMetadata.controlled_list_item_image_id
        );
        const toUpdate = imageFromItem.metadata.find((m: ControlledListItemImageMetadata) => m.id === updatedMetadata.id);
        toUpdate.metadata_type = updatedMetadata.metadata_type;
        toUpdate.language_id = updatedMetadata.language_id;
        toUpdate.value = updatedMetadata.value;
    };
});

const removeImage = computed(() => {
    return (removedImage: ControlledListItemImage) => {
        const toDelete = item.value.images.findIndex(
            (i: ControlledListItemImage) => i.id === removedImage.id
        );
        item.value.images.splice(toDelete, 1);
    };
});

const iconLabel = (item: ControlledListItem) => {
    return item.guide ? $gettext("Guide Item") : $gettext("Indexable Item");
};

const addHeader = (event: FileUploadBeforeSendEvent) => {
    event.xhr.setRequestHeader("X-CSRFToken", Cookies.get("csrftoken"));
    event.formData.set("item_id", item.value.id);
};

const onUpload = (event: FileUploadUploadEvent) => {
    if (event.xhr.status !== 201) {
        return;
    }
    const newImage = JSON.parse(event.xhr.responseText);
    item.value.images.push(newImage);
};
</script>

<template>
    <span class="item-header">
        <LetterCircle
            v-if="item"
            :labelled="item"
        />
        <h3>{{ bestLabel(item, selectedLanguage.code).value }}</h3>
        <span class="item-type">{{ iconLabel(item) }}</span>
        <a
            v-if="item.uri"
            :href="item.uri"
            rel="noreferrer"
            target="_blank"
            style="font-size: small; color: blue;"
        >
            {{ item.uri }}
        </a>
    </span>
    <LabelEditor
        :type="PREF_LABEL"
        :item
        :append-item-label
        :remove-item-label
        :update-item-label
    />
    <LabelEditor
        :type="ALT_LABEL"
        :item
        :append-item-label
        :remove-item-label
        :update-item-label
    />
    <div class="field-editor-container">
        <h4>{{ $gettext("List Item URI") }}</h4>
        <p>
            {{ $gettext(
                "Optionally, provide a URI for your list item. Useful if your list item is formally defined in a thesaurus or authority document."
            ) }}
        </p>
        <ItemCharacteristic
            field="uri"
            label="URI"
        />
    </div>
    <div class="field-editor-container images-container">
        <h4>{{ $gettext("Images") }}</h4>
        <FileUpload
            accept="image/*"
            :url="arches.urls.controlled_list_item_image_add"
            :auto="true"
            :max-file-size="5e6"
            :file-limit="10"
            :preview-width="250"
            :with-credentials="true"
            name="item_image"
            @before-send="addHeader($event)"
            @upload="onUpload($event)"
        />
        <div class="images">
            <ImageEditor
                v-for="image in item.images"
                :key="image.id"
                :image="image"
                :remove-image
                :append-image-metadata
                :remove-image-metadata
                :update-image-metadata
            />
            <span
                v-if="!item.images.length"
                :style="{ fontSize: 'small'}"
            >
                {{ $gettext("No images.") }}
            </span>
        </div>
    </div>
</template>

<style scoped>
.item-header {
    display: inline-flex;
    align-items: center;
    gap: 1rem;
    margin: 1rem 1rem 0rem 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid;
    width: 100%;
}

h3 {
    font-size: 1.5rem;
    margin: 0;
}

h4 {
    color: v-bind(slateBlue);
    margin-top: 0;
    font-size: small;
}

p {
    font-weight: normal;
    margin-top: 0;
    font-size: small;
}

.item-type {
    font-size: small;
    font-weight: 200;
}

.field-editor-container {
    margin: 1rem 1rem 3rem 1rem;
    display: flex;
    flex-direction: column;
}

.images-container {
    gap: 20px;
}

.images {
    display: flex;
    flex-direction: column;
    gap: 32px;
}

:deep(input[type=file]) {
    /* override arches.css */
    /* PrimeVue uses a hidden input for screen readers */
    display: none;
}
</style>
