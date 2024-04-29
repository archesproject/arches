<script setup lang="ts">
import arches from "arches";
import { computed, inject, ref } from "vue";
import { useGettext } from "vue3-gettext";

import Column from "primevue/column";
import Dropdown from "primevue/dropdown";
import DataTable from "primevue/datatable";
import InputText from "primevue/inputtext";
import { useToast } from "primevue/usetoast";

import AddMetadata from "@/components/ControlledListManager/AddMetadata.vue";

import { itemKey } from "@/components/ControlledListManager/const.ts";
import { bestLabel, languageName } from "@/components/ControlledListManager/utils.ts";

import type { ControlledListItemImage } from "@/types/ControlledListManager";
const { image } : {image: ControlledListItemImage} = defineProps(["image"]);
const { item } = inject(itemKey);

const editingRows = ref([]);

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

const saveMetadata = () => {
};

const deleteMetadata = () => {
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
                @row-edit-save="saveMetadata"
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
                            @click="deleteMetadata(slotProps.data)"
                            @key.enter="deleteMetadata(slotProps.data)"
                        />
                    </template>
                </Column>
            </DataTable>
            <AddMetadata
                :image
                :choices="METADATA_CHOICES"
            />
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
</style>
