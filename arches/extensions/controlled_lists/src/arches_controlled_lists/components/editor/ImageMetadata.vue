<script setup lang="ts">
import arches from "arches";
import { computed, inject, ref, useTemplateRef } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import InputText from "primevue/inputtext";
import Select from "primevue/select";
import { useToast } from "primevue/usetoast";

import {
    deleteImage,
    deleteMetadata,
    upsertMetadata,
} from "@/arches_controlled_lists/api.ts";
import {
    CONTRAST,
    DANGER,
    DEFAULT_ERROR_TOAST_LIFE,
    ERROR,
    METADATA_CHOICES,
    isEditingKey,
    itemKey,
} from "@/arches_controlled_lists/constants.ts";
import {
    commandeerFocusFromDataTable,
    dataIsNew,
    languageNameFromCode,
    shouldUseContrast,
} from "@/arches_controlled_lists/utils.ts";
import AddMetadata from "@/arches_controlled_lists/components/editor/AddMetadata.vue";

import type { Ref } from "vue";
import type { DataTableRowEditInitEvent } from "primevue/datatable";
import type {
    ControlledListItem,
    ControlledListItemImage,
    ControlledListItemImageMetadata,
    IsEditingRefAndSetter,
    LabeledChoice,
    Language,
    NewOrExistingControlledListItemImageMetadata,
} from "@/arches_controlled_lists/types";

const toast = useToast();
const { $gettext } = useGettext();

const metadataTypeHeader = $gettext("Metadata type");
const metadataValueHeader = $gettext("Value");
const languageHeader = $gettext("Language");

const item = inject(itemKey) as Ref<ControlledListItem>;
const { isEditing, setIsEditing } = inject(
    isEditingKey,
) as IsEditingRefAndSetter;
const { image } = defineProps<{ image: ControlledListItemImage }>();
const editingRows = ref<NewOrExistingControlledListItemImageMetadata[]>([]);
const rowIndexToFocus = ref(-1);
const editorDiv = useTemplateRef("editorDiv");

const labeledChoices: LabeledChoice[] = [
    {
        type: METADATA_CHOICES.title,
        label: $gettext("Title"),
    },
    {
        type: METADATA_CHOICES.alternativeText,
        label: $gettext("Alternative text"),
    },
    {
        type: METADATA_CHOICES.description,
        label: $gettext("Description"),
    },
    {
        type: METADATA_CHOICES.attribution,
        label: $gettext("Attribution"),
    },
];

const cursorClass = computed(() => {
    return isEditing.value ? "text" : "pointer";
});

const inputSelector = computed(() => {
    return `[data-p-index="${rowIndexToFocus.value}"]`;
});

const metadataLabel = (metadataType: string) => {
    return labeledChoices.find((choice) => choice.type === metadataType)!.label;
};

const saveMetadata = async (event: DataTableRowEditInitEvent) => {
    setIsEditing(editingRows.value.length > 0);
    // normalize new metadata numbers to null
    const normalizedNewData: NewOrExistingControlledListItemImageMetadata = {
        ...event.newData,
        id: dataIsNew(event.newData) ? null : event.newData.id,
    };
    let upsertedMetadata: ControlledListItemImageMetadata;
    try {
        upsertedMetadata = await upsertMetadata(normalizedNewData);
    } catch (error) {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("Metadata save failed"),
            detail: error instanceof Error ? error.message : undefined,
        });
        if (normalizedNewData.id === null) {
            removeImageMetadata(event.newData);
        }
        return;
    }
    if (normalizedNewData.id) {
        updateImageMetadata(upsertedMetadata);
    } else {
        appendImageMetadata(upsertedMetadata);
        removeImageMetadata(event.newData);
    }
};

const issueDeleteMetadata = async (
    metadata: ControlledListItemImageMetadata,
) => {
    makeRowUneditable(metadata.id);
    if (dataIsNew(metadata)) {
        removeImageMetadata(metadata);
        return;
    }
    try {
        await deleteMetadata(metadata);
    } catch (error) {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("Metadata deletion failed"),
            detail: error instanceof Error ? error.message : undefined,
        });
        return;
    }
    removeImageMetadata(metadata);
};

const appendImageMetadata = (newMetadata: ControlledListItemImageMetadata) => {
    const imageFromItem = item.value.images.find(
        (imageCandidateFromItem) =>
            imageCandidateFromItem.id === newMetadata.list_item_image_id,
    );
    if (imageFromItem) {
        imageFromItem.metadata.push(newMetadata);
    }
};

const removeImageMetadata = (
    removedMetadata: NewOrExistingControlledListItemImageMetadata,
) => {
    const imageFromItem = item.value.images.find(
        (imageCandidateFromItem) =>
            imageCandidateFromItem.id === removedMetadata.list_item_image_id,
    );
    if (imageFromItem) {
        const toDelete = imageFromItem.metadata.findIndex(
            (metadatum) => metadatum.id === removedMetadata.id,
        );
        if (toDelete === -1) {
            return;
        }
        imageFromItem.metadata.splice(toDelete, 1);
    }
};

const updateImageMetadata = (
    updatedMetadata: ControlledListItemImageMetadata,
) => {
    const imageFromItem = item.value.images.find(
        (imageCandidateFromItem) =>
            imageCandidateFromItem.id === updatedMetadata.list_item_image_id,
    );
    if (imageFromItem) {
        const toUpdate = imageFromItem.metadata.find(
            (metadatum) => metadatum.id === updatedMetadata.id,
        );
        if (!toUpdate) {
            return;
        }
        toUpdate.metadata_type = updatedMetadata.metadata_type;
        toUpdate.language_id = updatedMetadata.language_id;
        toUpdate.value = updatedMetadata.value;
    }
};

const issueDeleteImage = async () => {
    setIsEditing(false);
    try {
        await deleteImage(image);
    } catch (error) {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("Image deletion failed"),
            detail: error instanceof Error ? error.message : undefined,
        });
        return;
    }
    removeImage(image);
};

const removeImage = (removedImage: ControlledListItemImage) => {
    const toDelete = item.value.images.findIndex(
        (imageFromItem) => imageFromItem.id === removedImage.id,
    );
    item.value.images.splice(toDelete, 1);
};

const makeMetadataEditable = (
    clickedMetadata: NewOrExistingControlledListItemImageMetadata,
    index: number,
) => {
    if (isEditing.value) {
        return;
    }
    setIsEditing(true);
    if (!editingRows.value.includes(clickedMetadata)) {
        editingRows.value = [...editingRows.value, clickedMetadata];
    }
    if (index === -1) {
        // Coming from <AddMetadata>
        rowIndexToFocus.value = Math.max(image.metadata.length - 1, 0);
    } else {
        rowIndexToFocus.value = index;
    }
};

const setRowFocus = (event: DataTableRowEditInitEvent) => {
    if (isEditing.value) {
        return;
    }
    setIsEditing(true);
    rowIndexToFocus.value = event.index;
};

function makeRowUneditable(metadataId: string) {
    editingRows.value = [
        ...editingRows.value.filter((metadatum) => metadatum.id !== metadataId),
    ];
    setIsEditing(editingRows.value.length > 0);
}

const focusInput = () => {
    setIsEditing(true);
    if (rowIndexToFocus.value !== -1) {
        const rowEl = editorDiv.value!.querySelector(inputSelector.value);
        const inputEl = rowEl!.children[1].children[0] as HTMLInputElement;
        commandeerFocusFromDataTable(inputEl);
        rowIndexToFocus.value = -1;
    }
};
</script>

<template>
    <div ref="editorDiv">
        <DataTable
            v-if="image.metadata.length"
            v-model:editing-rows="editingRows"
            :value="image.metadata"
            data-key="id"
            edit-mode="row"
            striped-rows
            :style="{ fontSize: 'small' }"
            @row-edit-cancel="(event) => makeRowUneditable(event.data.id)"
            @row-edit-init="setRowFocus"
            @row-edit-save="saveMetadata"
        >
            <Column
                field="metadata_type"
                :header="metadataTypeHeader"
                style="width: 20%"
            >
                <template #editor="{ data, field }">
                    <Select
                        v-model="data[field]"
                        :options="labeledChoices"
                        option-label="label"
                        option-value="type"
                        :pt="{
                            root: { style: { width: '90%' } },
                            optionLabel: { style: { fontSize: 'small' } },
                        }"
                    />
                </template>
                <template #body="slotProps">
                    {{ metadataLabel(slotProps.data.metadata_type) }}
                </template>
            </Column>
            <Column
                field="value"
                :header="metadataValueHeader"
                style="width: 60%; min-width: 8rem"
            >
                <template #editor="{ data, field }">
                    <InputText
                        v-model="data[field]"
                        :pt="{
                            hooks: {
                                onMounted: focusInput,
                                onUpdated: focusInput,
                            },
                        }"
                    />
                </template>
                <template #body="slotProps">
                    <span
                        class="full-width-pointer"
                        style="white-space: pre-wrap"
                        @click.stop="
                            makeMetadataEditable(
                                slotProps.data,
                                slotProps.index,
                            )
                        "
                    >
                        {{ slotProps.data.value }}
                    </span>
                </template>
            </Column>
            <Column
                field="language_id"
                :header="languageHeader"
                style="width: 12%; height: 5rem"
            >
                <template #editor="{ data, field }">
                    <Select
                        v-model="data[field]"
                        :options="arches.languages"
                        :option-label="
                            (lang: Language) => `${lang.name} (${lang.code})`
                        "
                        option-value="code"
                        :pt="{ optionLabel: { style: { fontSize: 'small' } } }"
                    />
                </template>
                <template #body="slotProps">
                    {{
                        `${languageNameFromCode(slotProps.data.language_id)} (${slotProps.data.language_id})`
                    }}
                </template>
            </Column>
            <Column
                :row-editor="true"
                style="width: 5%; text-align: center; white-space: nowrap"
                :pt="{
                    headerCell: { ariaLabel: $gettext('Row edit controls') },
                }"
            >
                <template #roweditoriniticon>
                    <i
                        class="fa fa-pencil"
                        aria-hidden="true"
                    ></i>
                </template>
                <template #roweditorsaveicon>
                    <i
                        class="fa fa-check"
                        aria-hidden="true"
                    ></i>
                </template>
                <template #roweditorcancelicon>
                    <i
                        class="fa fa-undo"
                        aria-hidden="true"
                    ></i>
                </template>
            </Column>
            <Column
                style="width: 3%; text-align: center"
                :pt="{ headerCell: { ariaLabel: $gettext('Delete controls') } }"
            >
                <template #body="slotProps">
                    <i
                        class="fa fa-trash"
                        role="button"
                        tabindex="0"
                        :aria-label="$gettext('Delete')"
                        @click="issueDeleteMetadata(slotProps.data)"
                        @keyup.enter="issueDeleteMetadata(slotProps.data)"
                    />
                </template>
            </Column>
        </DataTable>
    </div>
    <div style="display: flex; gap: 0.5rem">
        <AddMetadata
            :image
            :labeled-choices
            :make-metadata-editable
        />
        <Button
            :severity="shouldUseContrast() ? CONTRAST : DANGER"
            icon="fa fa-trash"
            :label="$gettext('Delete')"
            @click="issueDeleteImage"
        />
    </div>
</template>

<style scoped>
.full-width-pointer {
    cursor: v-bind(cursorClass);
    display: flex;
    width: 100%;
}

:deep(td > input) {
    width: 100%;
    height: 3rem;
    font-size: inherit;
}

.p-button {
    height: 3rem;
    margin-top: 1rem;
    font-size: smaller;
}

:deep(.p-datatable-column-title) {
    font-size: small;
}

i {
    font-size: var(--p-icon-size);
}

:deep(.p-button-text.p-button-secondary.p-datatable-row-editor-save) {
    background: var(--p-button-secondary-background);
    border: 1px solid var(--p-button-secondary-border-color);
    border-radius: 50%;
}

:deep(.p-button-text.p-button-secondary.p-datatable-row-editor-save:hover) {
    background: var(--p-button-primary-hover-background);
    color: var(--p-button-primary-hover-color);
}

:deep(.p-button-text.p-button-secondary.p-datatable-row-editor-init) {
    background: var(--p-button-secondary-background);
    border: 1px solid var(--p-button-secondary-border-color);
    border-radius: 50%;
}

:deep(.p-button-text.p-button-secondary.p-datatable-row-editor-init:hover) {
    background: var(--p-button-primary-hover-background);
    color: var(--p-button-primary-hover-color);
}

:deep(.p-button-text.p-button-secondary.p-datatable-row-editor-cancel) {
    background: var(--p-button-secondary-background);
    border: 1px solid var(--p-button-secondary-border-color);
    border-radius: 50%;
}

:deep(.p-button-text.p-button-secondary.p-datatable-row-editor-cancel:hover) {
    background: var(--p-amber-300);
    color: var(--p-button-primary-hover-color);
}

:deep(i[role="button"]) {
    height: var(--p-button-icon-only-width);
    width: var(--p-button-icon-only-width);
    border-radius: 50%;
    border: 1px solid var(--p-button-secondary-border-color);
    background: var(--p-button-secondary-background);
    padding: 0.67rem;
}

:deep(i[role="button"]:hover) {
    background: var(--p-button-danger-background);
    color: var(--p-button-primary-hover-color);
}
</style>
