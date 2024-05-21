<script setup lang="ts">
import arches from "arches";
import { computed, inject, ref } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import Column from "primevue/column";
import Dropdown from "primevue/dropdown";
import DataTable from "primevue/datatable";
import InputText from "primevue/inputtext";
import { useToast } from "primevue/usetoast";

import AddMetadata from "@/components/ControlledListManager/AddMetadata.vue";

import { DANGER, METADATA_CHOICES, itemKey } from "@/components/ControlledListManager/constants.ts";
import { deleteImage, upsertMetadata, deleteMetadata } from "@/components/ControlledListManager/api.ts";
import { bestLabel, languageName } from "@/components/ControlledListManager/utils.ts";

import type { Ref } from "vue";
import type { DataTableRowEditInitEvent } from "primevue/datatable";
import type {
    ControlledListItem,
    ControlledListItemImage,
    ControlledListItemImageMetadata,
    NewControlledListItemImageMetadata,
    NewOrExistingControlledListItemImageMetadata,
} from "@/types/ControlledListManager";

const { image } = defineProps<{ image: ControlledListItemImage }>();
const item = inject(itemKey) as Ref<ControlledListItem>;

const editingRows = ref([]);

const toast = useToast();
const { $gettext } = useGettext();
const metadataTypeHeader = $gettext('Metadata type');
const languageHeader = $gettext('Language');

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

const onSaveMetadata = async (event: DataTableRowEditInitEvent)  => {
    // normalize new metadata numbers (starting at 1000) to null
    const normalizedNewData: ControlledListItemImageMetadata = {
        ...event.newData,
        id: typeof event.newData.id === 'string' ? event.newData.id : null,
    };
    const upsertedMetadata: ControlledListItemImageMetadata = await upsertMetadata(
        normalizedNewData,
        toast,
        $gettext,
    );
    if (upsertedMetadata) {
        if (normalizedNewData.id) {
            updateImageMetadata(upsertedMetadata);
        } else {
            appendImageMetadata(upsertedMetadata);
            removeImageMetadata(event.newData);
        }
    }
};

const onDeleteMetadata = async (metadata: NewControlledListItemImageMetadata | ControlledListItemImageMetadata) => {
    if (typeof metadata.id === 'number') {
        removeImageMetadata(metadata);
        return;
    }
    const deleted = await deleteMetadata(metadata, toast, $gettext);
    if (deleted) {
        removeImageMetadata(metadata);
    }
};

const onDeleteImage = async () => {
    const deleted = await deleteImage(image, toast, $gettext);
    if (deleted) {
        removeImage(image);
    }
};

const appendImageMetadata = (newMetadata: ControlledListItemImageMetadata) => {
    const imageFromItem = item.value!.images.find(
        (imageCandidateFromItem) =>
            imageCandidateFromItem.id === newMetadata.controlled_list_item_image_id
    );
    if (imageFromItem) {
        imageFromItem.metadata.push(newMetadata);
    }
};

const removeImageMetadata = (removedMetadata: NewOrExistingControlledListItemImageMetadata) => {
    const imageFromItem = item.value!.images.find(
        (imageCandidateFromItem) =>
            imageCandidateFromItem.id === removedMetadata.controlled_list_item_image_id
    );
    if (imageFromItem) {
        const toDelete = imageFromItem.metadata.findIndex(
            (metadatum) => metadatum.id === removedMetadata.id
        );
        if (toDelete === -1) {
            return;
        }
        imageFromItem.metadata.splice(toDelete, 1);
    }
};

const updateImageMetadata = (updatedMetadata: ControlledListItemImageMetadata) => {
    const imageFromItem = item.value!.images.find(
        (imageCandidateFromItem) =>
            imageCandidateFromItem.id === updatedMetadata.controlled_list_item_image_id
    );
    if (imageFromItem) {
        const toUpdate = imageFromItem.metadata.find(
            (metadatum) => metadatum.id === updatedMetadata.id
        );
        if (!toUpdate) {
            return;
        }
        toUpdate.metadata_type = updatedMetadata.metadata_type;
        toUpdate.language_id = updatedMetadata.language_id;
        toUpdate.value = updatedMetadata.value;
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
            <DataTable
                v-if="image.metadata.length"
                v-model:editingRows="editingRows"
                :value="image.metadata"
                data-key="id"
                edit-mode="row"
                striped-rows
                :style="{ fontSize: 'small' }"
                @row-edit-save="onSaveMetadata"
            >
                <Column
                    field="metadata_type"
                    :header="metadataTypeHeader"
                    style="width: 20%;"
                >
                    <template #editor="{ data, field }">
                        <Dropdown
                            v-model="data[field]"
                            :options="labeledMetadataChoices"
                            option-label="label"
                            option-value="type"
                            :pt="{
                                root: { style: { width: '90%' } },
                                input: { style: { fontFamily: 'inherit', fontSize: 'small' } },
                                panel: { style: { fontSize: 'small' } },
                            }"
                        />
                    </template>
                    <template #body="slotProps">
                        {{ labeledMetadataChoices.find(choice => choice.type === slotProps.data.metadata_type).label }}
                    </template>
                </Column>
                <Column
                    field="value"
                    style="width: 60%; min-width: 8rem;"
                >
                    <template #editor="{ data, field }">
                        <InputText v-model="data[field]" />
                    </template>
                </Column>
                <Column
                    field="language_id"
                    :header="languageHeader"
                    style="width: 10%; min-width: 8rem; height: 4rem; padding-left: 1rem;"
                >
                    <template #editor="{ data, field }">
                        <Dropdown
                            v-model="data[field]"
                            :options="arches.languages"
                            option-label="name"
                            option-value="code"
                            :pt="{
                                input: { style: { fontFamily: 'inherit', fontSize: 'small' } },
                                panel: { style: { fontSize: 'small' } },
                            }"
                        />
                    </template>
                    <template #body="slotProps">
                        {{ languageName(slotProps.data.language_id) }}
                    </template>
                </Column>
                <Column
                    :row-editor="true"
                    style="width: 5%; min-width: 8rem; text-align: center;"
                />
                <Column style="width: 5%; text-align: center;">
                    <template #body="slotProps">
                        <i
                            class="fa fa-trash"
                            role="button"
                            tabindex="0"
                            :aria-label="$gettext('Delete')"
                            @click="onDeleteMetadata(slotProps.data)"
                            @key.enter="onDeleteMetadata(slotProps.data)"
                        />
                    </template>
                </Column>
            </DataTable>
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
:deep(th) {
    font-weight: 600;
}
:deep(td:first-child) {
    padding-left: 0.75rem;
}
:deep(td > input) {
    width: 95%;
}
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
