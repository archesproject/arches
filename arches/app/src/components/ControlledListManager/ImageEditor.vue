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

import { itemKey } from "@/components/ControlledListManager/const.ts";
import { deleteImage, upsertMetadata, deleteMetadata } from "@/components/ControlledListManager/api.ts";
import { bestLabel, languageName } from "@/components/ControlledListManager/utils.ts";

import type { DataTableRowEditInitEvent } from "primevue/datatable";
import type {
    ControlledListItemImage,
    ControlledListItemImageMetadata,
    NewControlledListItemImageMetadata,
} from "@/types/ControlledListManager";

const { image, removeImage, appendImageMetadata, updateImageMetadata, removeImageMetadata } : {
    image: ControlledListItemImage,
    removeImage: (removedImage: ControlledListItemImage) => undefined,
    appendImageMetadata: (appendedMetadata: ControlledListItemImageMetadata | NewControlledListItemImageMetadata) => undefined,
    updateImageMetadata: (updatedMetadata: ControlledListItemImageMetadata) => undefined,
    removeImageMetadata: (removedMetadata: ControlledListItemImageMetadata | NewControlledListItemImageMetadata) => undefined,
} = defineProps(["image", "removeImage", "appendImageMetadata", "updateImageMetadata", "removeImageMetadata"]);
const { item } = inject(itemKey);

const editingRows = ref([]);

const DANGER = "danger";
const toast = useToast();
const { $gettext } = useGettext();

const METADATA_CHOICES = [
    {
        type: 'title',
        label: $gettext('Title'),
    },
    {
        type: 'alt',
        label: $gettext('Alternative text'),
    },
    {
        type: 'desc',
        label: $gettext('Description'),
    },
    {
        type: 'attr',
        label: $gettext('Attribution'),
    },
];

const bestAlternativeText = computed(() => {
    return image.metadata.filter(m => m.metadata_type === "alt")
        .find(m => m.language_id === arches.activeLanguage)?.value
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
    if (normalizedNewData.id) {
        updateImageMetadata(upsertedMetadata);
    } else {
        appendImageMetadata(upsertedMetadata);
        removeImageMetadata(event.newData);
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
</script>

<template>
    <div>
        <img
            :src="image.url"
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
                    :header="$gettext('Metadata type')"
                >
                    <template #editor="{ data, field }">
                        <Dropdown
                            v-model="data[field]"
                            :options="METADATA_CHOICES"
                            option-label="label"
                            option-value="type"
                            :pt="{
                                input: { style: { fontFamily: 'inherit', fontSize: 'small' } },
                                panel: { style: { fontSize: 'small' } },
                            }"
                        />
                    </template>
                    <template #body="slotProps">
                        {{ METADATA_CHOICES.find(choice => choice.type === slotProps.data.metadata_type).label }}
                    </template>
                </Column>
                <Column field="value">
                    <template #editor="{ data, field }">
                        <InputText
                            v-model="data[field]"
                            style="width: 75%"
                        />
                    </template>
                </Column>
                <Column
                    field="language_id"
                    :header="$gettext('Language')"
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
                    style="width: 10%; min-width: 8rem;"
                />
                <Column style="width: 5%;">
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
                    :choices="METADATA_CHOICES"
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
:deep(td) {
    padding-left: 0.75rem;
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
