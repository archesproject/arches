<script setup lang="ts">
import arches from "arches";
import { computed, inject, ref } from "vue";
import { useGettext } from "vue3-gettext";

import Column from "primevue/column";
import DataTable from "primevue/datatable";
import Dropdown from "primevue/dropdown";
import InputText from "primevue/inputtext";
import { useToast } from "primevue/usetoast";

import { deleteValue, upsertValue } from "@/components/ControlledListManager/api.ts";
import AddValue from "@/components/ControlledListManager/AddValue.vue";

import { ALT_LABEL, NOTE, PREF_LABEL, itemKey } from "@/components/ControlledListManager/constants.ts";
import { languageName } from "@/components/ControlledListManager/utils.ts";

import { ARCHES_CHROME_BLUE } from "@/theme.ts";

import type { Ref } from "vue";
import type { DataTableRowEditInitEvent } from "primevue/datatable";
import type {
    ControlledListItem,
    Value,
    ValueCategory,
    NewValue,
    ValueType,
} from "@/types/ControlledListManager";

const { valueType, valueCategory } = defineProps<{
    valueType?: ValueType;
    valueCategory?: ValueCategory;

}>();
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
                heading: $gettext("Notes"),
                subheading: $gettext("Optionally, you can provide notes for your list item."),
            };
    }
});

const values = computed(() => {
    if (!item.value) {
        return [];
    }
    if (!valueType) {
        if (valueCategory === NOTE) {
        // Show everything but labels for now. We're not returning category from the API.
            return item.value.values.filter(
                value => ![PREF_LABEL, ALT_LABEL].includes(value.valuetype_id)
            );
        }
    }
    return item.value.values.filter(
        value => value.valuetype_id === valueType
    );
});

const onSave = async (event: DataTableRowEditInitEvent) => {
    // normalize new value numbers (starting at 1000) to null
    const normalizedNewData: Value = {
        ...event.newData,
        id: typeof event.newData.id === 'string' ? event.newData.id : null,
    };
    const upsertedValue: Value = await upsertValue(
        normalizedNewData,
        toast,
        $gettext,
    );
    if (upsertedValue) {
        if (normalizedNewData.id) {
            updateItemValue(upsertedValue);
        } else {
            appendItemValue(upsertedValue);
            removeItemValue(event.newData);
        }
    }
};

const onDelete = async (value: NewValue | Value) => {
    if (typeof value.id === 'number') {
        removeItemValue(value);
        return;
    }
    const deleted = await deleteValue(value, toast, $gettext);
    if (deleted) {
        removeItemValue(value);
    }
};

const appendItemValue = (newValue: Value) => { item.value.values.push(newValue); };

const removeItemValue = (removedValue: Value | NewValue) => {
    const toDelete = item.value.values.findIndex(valueFromItem => valueFromItem.id === removedValue.id);
    item.value.values.splice(toDelete, 1);
};

const updateItemValue = (updatedValue: Value) => {
    const toUpdate = item.value.values.find(valueFromItem => valueFromItem.id === updatedValue.id);
    if (toUpdate) {
        toUpdate.language_id = updatedValue.language_id;
        toUpdate.value = updatedValue.value;
    }
};
</script>

<template>
    <div class="value-editor-container">
        <h4>{{ headings.heading }}</h4>
        <p>{{ headings.subheading }}</p>
        <DataTable
            v-if="values.length"
            v-model:editingRows="editingRows"
            :value="values"
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
        <AddValue :value-type />
    </div>
</template>

<style scoped>
.value-editor-container {
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
