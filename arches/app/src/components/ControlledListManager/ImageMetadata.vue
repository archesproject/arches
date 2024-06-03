<script setup lang="ts">
import arches from "arches";
import { computed, ref, inject } from "vue";
import { useGettext } from "vue3-gettext";

import Column from "primevue/column";
import Dropdown from "primevue/dropdown";
import DataTable from "primevue/datatable";
import InputText from "primevue/inputtext";
import { useToast } from "primevue/usetoast";

import { upsertMetadata, deleteMetadata } from "@/components/ControlledListManager/api.ts";
import { itemKey } from "@/components/ControlledListManager/constants.ts";
import { languageName } from "@/components/ControlledListManager/utils.ts";

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

const metadataTypeHeader = $gettext('Metadata type');
const languageHeader = $gettext('Language');

const item = inject(itemKey) as Ref<ControlledListItem>;
const { labeledChoices, metadata } = defineProps<{
    labeledChoices: LabeledChoice[];
    metadata: ControlledListItemImageMetadata[];
}>();
const editingRows: Ref<ControlledListItemImageMetadata[]> = ref([]);
const rowIndexToFocus: Ref<number> = ref(-1);
const editorRef: Ref<HTMLDivElement | null> = ref(null); 

const metadataLabel = (metadataType: string) => {
    return labeledChoices.find(choice => choice.type === metadataType)!.label;
};

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
    } else if (normalizedNewData.id === null) {
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

const onEdit = (event: DataTableRowEditInitEvent) => {
    rowIndexToFocus.value = event.index;
};

const makeValueEditable = (clickedValue: ControlledListItemImageMetadata, index: number) => {
    if (!editingRows.value.includes(clickedValue)) {
        editingRows.value = [ ...editingRows.value, clickedValue ];
    }
    rowIndexToFocus.value = index;
};

const inputSelector = computed(() => {
    return `[data-p-index="${rowIndexToFocus.value}"]`;
});

const focusInput = () => {
    // The editor (pencil) button immediately hogs focus with a setTimeout of 1,
    // so we'll get in line behind it to set focus to the input.
    setTimeout(() => {
        if (rowIndexToFocus.value !== -1) {
            const editorDiv = editorRef.value;
            const rowEl = editorDiv!.querySelector(inputSelector.value);
            const inputEl = rowEl!.children[1].children[0];
            // @ts-expect-error focusVisible not yet in typeshed
            inputEl.focus({ focusVisible: true });
        }
        rowIndexToFocus.value = -1;
    }, 2);
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
            @row-edit-init="onEdit"
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
                        :options="labeledChoices"
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
                    {{ metadataLabel(slotProps.data.metadata_type) }}
                </template>
            </Column>
            <Column
                field="value"
                style="width: 60%; min-width: 8rem;"
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
                        @click.stop="makeValueEditable(slotProps.data, slotProps.index)"
                    >
                        {{ slotProps.data.value }}
                    </span>
                </template>
            </Column>
            <Column
                field="language_id"
                :header="languageHeader"
                style="width: 10%; min-width: 8rem; height: 5rem; padding-left: 1rem;"
            >
                <template #editor="{ data, field }">
                    <Dropdown
                        v-model="data[field]"
                        :options="arches.languages"
                        :option-label="(lang) => `${lang.name} (${lang.code})`"
                        option-value="code"
                        :pt="{
                            input: { style: { fontFamily: 'inherit', fontSize: 'small' } },
                            panel: { style: { fontSize: 'small' } },
                        }"
                    />
                </template>
                <template #body="slotProps">
                    {{ `${languageName(slotProps.data.language_id)} (${slotProps.data.language_id})` }}
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
