<script setup lang="ts">
import arches from "arches";
import { computed, inject } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";

import { ARCHES_CHROME_BLUE } from "@/theme.ts";
import {
    itemKey,
    ALT_LABEL,
    NOTE_CHOICES,
    PREF_LABEL,
} from "@/components/ControlledListManager/constants.ts";

import type { Ref } from "vue";
import type { Language } from "@/types/arches";
import type {
    ControlledListItem,
    Value,
    NewValue,
    ValueType,
} from "@/types/ControlledListManager";

const { valueType, makeNewValueEditable } = defineProps<{
    valueType?: ValueType;
    makeNewValueEditable: (newValue: NewValue, index: number) => void;
}>();
const item = inject(itemKey) as Ref<ControlledListItem>;

const { $gettext } = useGettext();

const newValue: Ref<NewValue> = computed(() => {
    const otherNewValueIds = item.value.values
        .filter((value: NewValue | Value) => typeof value.id === "number")
        .map((value) => value.id as number);

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
        id: maxOtherNewValueId + 1,
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
        @click="addValue"
    >
        <i
            class="fa fa-plus-circle"
            aria-hidden="true"
        />
        <span class="add-value-text">
            {{ buttonLabel }}
        </span>
    </Button>
</template>

<style scoped>
.add-value {
    display: flex;
    height: 3rem;
    color: v-bind(ARCHES_CHROME_BLUE);
    background-color: #f3fbfd;
    margin-top: 1rem;
}
.add-value > i,
.add-value > span {
    align-self: center;
}
.add-value-text {
    margin: 1rem;
    font-size: small;
    font-weight: 600;
}
</style>
