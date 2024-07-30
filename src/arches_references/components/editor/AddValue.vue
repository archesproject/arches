<script setup lang="ts">
import arches from "arches";
import { computed, inject } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";

import {
    itemKey,
    ALT_LABEL,
    CONTRAST,
    NOTE_CHOICES,
    PREF_LABEL,
    PRIMARY,
} from "@/arches_references/constants.ts";
import { dataIsNew, shouldUseContrast } from "@/arches_references/utils.ts";

import type { Ref } from "vue";
import type { Language } from "@/arches/types";
import type {
    ControlledListItem,
    Value,
    ValueType,
} from "@/arches_references/types";

const { valueType, makeNewValueEditable } = defineProps<{
    valueType?: ValueType;
    makeNewValueEditable: (newValue: Value, index: number) => void;
}>();
const item = inject(itemKey) as Ref<ControlledListItem>;

const { $gettext } = useGettext();

const newValue: Ref<Value> = computed(() => {
    const otherNewValueIds = item.value.values
        .filter((value: Value) => dataIsNew(value))
        .map((value) => Number.parseInt(value.id));

    const maxOtherNewValueId = Math.max(...otherNewValueIds, 0);

    let nextLanguageCode = arches.activeLanguage;
    if (valueType === PREF_LABEL) {
        const maybeNextLanguage = arches.languages.find(
            (lang: Language) =>
                !item.value.values
                    .map((val) => val.language_id)
                    .includes(lang.code),
        );
        if (maybeNextLanguage) {
            nextLanguageCode = maybeNextLanguage.code;
        }
    }

    let nextValueType = valueType;
    if (!nextValueType) {
        const otherUsedValueTypes = item.value.values
            .map((value) => value.valuetype_id)
            .filter(
                (typeid) =>
                    // Labels handled separately.
                    ![PREF_LABEL, ALT_LABEL].includes(typeid),
            );
        for (const choice of Object.values(NOTE_CHOICES)) {
            if (!otherUsedValueTypes.includes(choice as string)) {
                nextValueType = choice as string;
                break;
            }
        }
    }

    return {
        id: (maxOtherNewValueId + 1).toString(),
        valuetype_id: nextValueType ?? NOTE_CHOICES.scope,
        language_id: nextLanguageCode,
        value: "",
        list_item_id: item.value.id,
    };
});

const buttonLabel = computed(() => {
    switch (valueType) {
        case PREF_LABEL:
            return $gettext("Add Preferred Label");
        case ALT_LABEL:
            return $gettext("Add Alternate Label");
        default:
            return $gettext("Add Note");
    }
});

const addValue = () => {
    const staticNewValue = newValue.value;
    item.value.values.push(staticNewValue);
    makeNewValueEditable(staticNewValue, -1);
};
</script>

<template>
    <Button
        class="add-value"
        raised
        icon="fa fa-plus-circle"
        :severity="shouldUseContrast() ? CONTRAST : PRIMARY"
        :label="buttonLabel"
        @click="addValue"
    />
</template>

<style scoped>
.add-value {
    display: flex;
    height: 3rem;
    margin-top: 1rem;
    font-size: smaller;
}
</style>
