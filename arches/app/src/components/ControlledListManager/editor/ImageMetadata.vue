<script setup lang="ts">
import arches from "arches";
import { computed, ref, inject } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import Column from "primevue/column";
import Dropdown from "primevue/dropdown";
import DataTable from "primevue/datatable";
import InputText from "primevue/inputtext";
import { useToast } from "primevue/usetoast";

import {
    deleteImage,
    deleteMetadata,
    upsertMetadata,
} from "@/components/ControlledListManager/api.ts";
import {
    DANGER,
    DEFAULT_ERROR_TOAST_LIFE,
    ERROR,
    METADATA_CHOICES,
    itemKey,
} from "@/components/ControlledListManager/constants.ts";
import { languageNameFromCode } from "@/components/ControlledListManager/utils.ts";
import AddMetadata from "@/components/ControlledListManager/editor/AddMetadata.vue";

import type { Ref } from "vue";
import type { DataTableRowEditInitEvent } from "primevue/datatable";
import type {
    ControlledListItem,
    ControlledListItemImage,
    ControlledListItemImageMetadata,
    LabeledChoice,
    NewOrExistingControlledListItemImageMetadata,
} from "@/types/ControlledListManager";

const toast = useToast();
const { $gettext } = useGettext();

const metadataTypeHeader = $gettext("Metadata type");
const metadataValueHeader = $gettext("Value");
const languageHeader = $gettext("Language");

const item = inject(itemKey) as Ref<ControlledListItem>;
const { image } = defineProps<{ image: ControlledListItemImage }>();
const editingRows = ref<NewOrExistingControlledListItemImageMetadata[]>([]);
const rowIndexToFocus = ref(-1);
const editorRef: Ref<HTMLDivElement | null> = ref(null);

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

const metadataLabel = (metadataType: string) => {
    return labeledChoices.find((choice) => choice.type === metadataType)!.label;
};

const saveMetadata = async (event: DataTableRowEditInitEvent) => {
    // normalize new metadata numbers to null
    const normalizedNewData: ControlledListItemImageMetadata = {
        ...event.newData,
        id: typeof event.newData.id === "string" ? event.newData.id : null,
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
    metadata: NewOrExistingControlledListItemImageMetadata,
) => {
    if (typeof metadata.id === "number") {
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
    const imageFromItem = item.value!.images.find(
        (imageCandidateFromItem) =>
            imageCandidateFromItem.id ===
            newMetadata.controlled_list_item_image_id,
    );
    if (imageFromItem) {
        imageFromItem.metadata.push(newMetadata);
    }
};

const removeImageMetadata = (
    removedMetadata: NewOrExistingControlledListItemImageMetadata,
) => {
    const imageFromItem = item.value!.images.find(
        (imageCandidateFromItem) =>
            imageCandidateFromItem.id ===
            removedMetadata.controlled_list_item_image_id,
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
    const imageFromItem = item.value!.images.find(
        (imageCandidateFromItem) =>
            imageCandidateFromItem.id ===
            updatedMetadata.controlled_list_item_image_id,
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
    const toDelete = item.value!.images.findIndex(
        (imageFromItem) => imageFromItem.id === removedImage.id,
    );
    item.value!.images.splice(toDelete, 1);
};

const makeMetadataEditable = (
    clickedMetadata: NewOrExistingControlledListItemImageMetadata,
    index: number,
) => {
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
    rowIndexToFocus.value = event.index;
};

const inputSelector = computed(() => {
    return `[data-p-index="${rowIndexToFocus.value}"]`;
});

const focusInput = () => {
    // The editor (pencil) button from the DataTable (elsewhere on page)
    // immediately hogs focus with a setTimeout of 1,
    // so we'll get in line behind it to set focus to the input.
    // This should be reported/clarified with PrimeVue with a MWE.
    setTimeout(() => {
        if (rowIndexToFocus.value !== -1) {
            const editorDiv = editorRef.value;
            const rowEl = editorDiv!.querySelector(inputSelector.value);
            const inputEl = rowEl!.children[1].children[0];
            // @ts-expect-error focusVisible not yet in typeshed
            (inputEl as HTMLInputElement).focus({ focusVisible: true });
        }
        rowIndexToFocus.value = -1;
    }, 25);
};
</script>

<template>
    <div ref="editorRef">
        <DataTable
            v-if="image.metadata.length"
            v-model:editingRows="editingRows"
            :value="image.metadata"
            data-key="id"
            edit-mode="row"
            striped-rows
            :style="{ fontSize: 'small' }"
            @row-edit-init="setRowFocus"
            @row-edit-save="saveMetadata"
        >
            <Column
                field="metadata_type"
                :header="metadataTypeHeader"
                style="width: 20%"
            >
                <template #editor="{ data, field }">
                    <Dropdown
                        v-model="data[field]"
                        :options="labeledChoices"
                        option-label="label"
                        option-value="type"
                        :pt="{
                            root: { style: { width: '90%' } },
                            input: {
                                style: {
                                    fontFamily: 'inherit',
                                    fontSize: 'small',
                                },
                            },
                            panel: { style: { fontSize: 'small' } },
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
                style="
                    width: 10%;
                    min-width: 8rem;
                    height: 5rem;
                    padding-left: 1rem;
                "
            >
                <template #editor="{ data, field }">
                    <Dropdown
                        v-model="data[field]"
                        :options="arches.languages"
                        :option-label="(lang) => `${lang.name} (${lang.code})`"
                        option-value="code"
                        :pt="{
                            input: {
                                style: {
                                    fontFamily: 'inherit',
                                    fontSize: 'small',
                                },
                            },
                            panel: { style: { fontSize: 'small' } },
                        }"
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
                style="width: 5%; min-width: 6rem; text-align: center"
                :pt="{
                    headerCell: { ariaLabel: $gettext('Row edit controls') },
                    rowEditorInitButton: {
                        class: 'fa fa-pencil',
                        style: { display: 'inline-flex' },
                    },
                    rowEditorInitIcon: { style: { display: 'none' } },
                    rowEditorSaveButton: {
                        class: 'fa fa-check',
                        style: { display: 'inline-flex' },
                    },
                    rowEditorSaveIcon: { style: { display: 'none' } },
                    rowEditorCancelButton: {
                        class: 'fa fa-undo',
                        style: { display: 'inline-flex' },
                    },
                    rowEditorCancelIcon: { style: { display: 'none' } },
                }"
            />
            <Column
                style="width: 5%; text-align: center"
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
    <div style="display: flex; gap: 1rem">
        <AddMetadata
            :image
            :labeled-choices
            :make-metadata-editable
        />
        <Button
            raised
            :severity="DANGER"
            icon="fa fa-trash"
            :label="$gettext('Delete image')"
            @click="issueDeleteImage"
        />
    </div>
</template>

<style scoped>
.full-width-pointer {
    cursor: pointer;
    display: flex;
    width: 100%;
}

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
