<script setup lang="ts">
import arches from "arches";
import { computed, ref, inject } from "vue";
import { useGettext } from "vue3-gettext";

import Column from "primevue/column";
import Dropdown from "primevue/dropdown";
import DataTable from "primevue/datatable";
import InputText from "primevue/inputtext";
import { useToast } from "primevue/usetoast";

import {
    upsertMetadata,
    deleteMetadata,
} from "@/components/ControlledListManager/api.ts";
import {
    DEFAULT_ERROR_TOAST_LIFE,
    ERROR,
    itemKey,
} from "@/components/ControlledListManager/constants.ts";
import { languageNameFromCode } from "@/components/ControlledListManager/utils.ts";

import type { Ref } from "vue";
import type { DataTableRowEditInitEvent } from "primevue/datatable";
import type {
    ControlledListItem,
    ControlledListItemImageMetadata,
    LabeledChoice,
    NewControlledListItemImageMetadata,
    NewOrExistingControlledListItemImageMetadata,
} from "@/types/ControlledListManager";

const toast = useToast();
const { $gettext } = useGettext();

const metadataTypeHeader = $gettext("Metadata type");
const metadataValueHeader = $gettext("Value");
const languageHeader = $gettext("Language");

const item = inject(itemKey) as Ref<ControlledListItem>;
const { labeledChoices, metadata } = defineProps<{
    labeledChoices: LabeledChoice[];
    metadata: ControlledListItemImageMetadata[];
}>();
const editingRows: Ref<ControlledListItemImageMetadata[]> = ref([]);
const rowIndexToFocus: Ref<number> = ref(-1);
const editorRef: Ref<HTMLDivElement | null> = ref(null);

const metadataLabel = (metadataType: string) => {
    return labeledChoices.find((choice) => choice.type === metadataType)!.label;
};

const saveMetadata = async (event: DataTableRowEditInitEvent) => {
    // normalize new metadata numbers (starting at 1000) to null
    const normalizedNewData: ControlledListItemImageMetadata = {
        ...event.newData,
        id: typeof event.newData.id === "string" ? event.newData.id : null,
    };
    try {
        const upsertedMetadata: ControlledListItemImageMetadata =
            await upsertMetadata(normalizedNewData);
        if (normalizedNewData.id) {
            updateImageMetadata(upsertedMetadata);
        } else {
            appendImageMetadata(upsertedMetadata);
            removeImageMetadata(event.newData);
        }
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
    }
};

const issueDeleteMetadata = async (
    metadata:
        | NewControlledListItemImageMetadata
        | ControlledListItemImageMetadata,
) => {
    if (typeof metadata.id === "number") {
        removeImageMetadata(metadata);
        return;
    }
    try {
        await deleteMetadata(metadata);
        removeImageMetadata(metadata);
    } catch (error) {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("Metadata deletion failed"),
            detail: error instanceof Error ? error.message : undefined,
        });
    }
};

const appendImageMetadata = (newMetadata: ControlledListItemImageMetadata) => {
    const imageFromItem = item.value!.images.find(
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
    const imageFromItem = item.value!.images.find(
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
    const imageFromItem = item.value!.images.find(
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

const setRowFocus = (event: DataTableRowEditInitEvent) => {
    rowIndexToFocus.value = event.index;
};

const makeValueEditable = (
    clickedValue: ControlledListItemImageMetadata,
    index: number,
) => {
    if (!editingRows.value.includes(clickedValue)) {
        editingRows.value = [...editingRows.value, clickedValue];
    }
    rowIndexToFocus.value = index;
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
    }, 5);
};
</script>

<template>
    <div ref="editorRef">
        <DataTable
            v-if="metadata.length"
            v-model:editingRows="editingRows"
            :value="metadata"
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
                        :pt="{ hooks: { onUpdated: focusInput } }"
                    />
                </template>
                <template #body="slotProps">
                    <span
                        class="full-width-pointer"
                        style="white-space: pre-wrap"
                        @click.stop="
                            makeValueEditable(slotProps.data, slotProps.index)
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
</style>
