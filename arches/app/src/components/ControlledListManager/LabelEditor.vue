<script setup lang="ts">
import arches from "arches";
import { computed, inject, ref } from "vue";
import { useGettext } from "vue3-gettext";

import Column from "primevue/column";
import DataTable from "primevue/datatable";
import Dropdown from "primevue/dropdown";
import InputText from "primevue/inputtext";
import { useToast } from "primevue/usetoast";

import { deleteLabel, upsertLabel } from "@/components/ControlledListManager/api.ts";
import AddLabel from "@/components/ControlledListManager/AddLabel.vue";

import { ALT_LABEL, PREF_LABEL, itemKey } from "@/components/ControlledListManager/constants.ts";
import { languageName } from "@/components/ControlledListManager/utils.ts";

import { ARCHES_CHROME_BLUE } from "@/theme.ts";

import type { Ref } from "vue";
import type { DataTableRowEditInitEvent } from "primevue/datatable";
import type {
    ControlledListItem,
    Label,
    NewLabel,
    ValueType,
} from "@/types/ControlledListManager";

const { valueType } = defineProps<{ valueType: ValueType }>();
const editingRows = ref([]);

const item = inject(itemKey) as Ref<ControlledListItem>;

const toast = useToast();
const { $gettext } = useGettext();
const languageHeader = $gettext('Language');

const headings: Ref<{ heading: string; subheading: string }> = computed(() => {
    switch (valueType) {
        case PREF_LABEL:
            return {
                heading: $gettext("Preferred Label(s)"),
                subheading: $gettext(
                    "Provide at least one preferred label and language for your list item."
                ),
            };
        case ALT_LABEL:
            return {
                heading: $gettext("Alternate Label(s)"),
                subheading: $gettext(
                    "Optionally, you can provide additional labels for your list item. Useful if you want to make searching for labels with synonyms or common misspellings of your preferred label(s) easier."
                ),
            };
        default:
            return {
                heading: "",
                subheading: "",
            };
    }
});

const labels = computed(() => {
    if (!item.value) {
        return [];
    }
    return item.value.labels.filter(
        label => label.valuetype_id === valueType
    );
});

const onSave = async (event: DataTableRowEditInitEvent) => {
    // normalize new label numbers (starting at 1000) to null
    const normalizedNewData: Label = {
        ...event.newData,
        id: typeof event.newData.id === 'string' ? event.newData.id : null,
    };
    const upsertedLabel: Label = await upsertLabel(
        normalizedNewData,
        toast,
        $gettext,
    );
    if (upsertedLabel) {
        if (normalizedNewData.id) {
            updateItemLabel(upsertedLabel);
        } else {
            appendItemLabel(upsertedLabel);
            removeItemLabel(event.newData);
        }
    }
};

const onDelete = async (label: NewLabel | Label) => {
    if (typeof label.id === 'number') {
        removeItemLabel(label);
        return;
    }
    const deleted = await deleteLabel(label, toast, $gettext);
    if (deleted) {
        removeItemLabel(label);
    }
};

const appendItemLabel = (newLabel: Label) => { item.value.labels.push(newLabel); };

const removeItemLabel = (removedLabel: Label | NewLabel) => {
    const toDelete = item.value.labels.findIndex(labelFromItem => labelFromItem.id === removedLabel.id);
    item.value.labels.splice(toDelete, 1);
};

const updateItemLabel = (updatedLabel: Label) => {
    const toUpdate = item.value.labels.find(labelFromItem => labelFromItem.id === updatedLabel.id);
    if (toUpdate) {
        toUpdate.language_id = updatedLabel.language_id;
        toUpdate.value = updatedLabel.value;
    }
};
</script>

<template>
    <div class="label-editor-container">
        <h4>{{ headings.heading }}</h4>
        <p>{{ headings.subheading }}</p>
        <DataTable
            v-if="labels.length"
            v-model:editingRows="editingRows"
            :value="labels"
            data-key="id"
            edit-mode="row"
            striped-rows
            scrollable
            :style="{ fontSize: 'small' }"
            @row-edit-save="onSave"
        >
            <Column
                field="value"
                style="min-width: 8rem"
            >
                <template #editor="{ data, field }">
                    <InputText v-model="data[field]" />
                </template>
            </Column>
            <Column
                field="language_id"
                :header="languageHeader"
                style="width: 10%; min-width: 8rem; height: 4rem"
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
                        @click="onDelete(slotProps.data)"
                        @key.enter="onDelete(slotProps.data)"
                    />
                </template>
            </Column>
        </DataTable>
        <AddLabel :type="valueType" />
    </div>
</template>

<style scoped>
.label-editor-container {
    margin: 1rem 1rem 3rem 1rem;
    width: 100%;
}

h4 {
    color: v-bind(ARCHES_CHROME_BLUE);
    margin-top: 0;
    font-size: small;
}

p {
    font-weight: normal;
    margin-top: 0;
    font-size: small;
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
