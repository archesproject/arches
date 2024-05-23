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
    LabeledChoice,
    Value,
    NewValue,
    ValueType,
} from "@/types/ControlledListManager";

const props = defineProps<{ valueType?: ValueType, labeledChoices: LabeledChoice[]; }>();
const item = inject(itemKey) as Ref<ControlledListItem>;

const { $gettext } = useGettext();

const newValue: Ref<NewValue> = computed(() => {
    const otherNewValueIds = item.value.values.filter(
        (value: NewValue | Value) => typeof value.id === "number"
    ).map(value => value.id as unknown as number);
    const maxOtherNewValueId = Math.max(
        ...otherNewValueIds,
        1000,
    );

    const nextLanguage = arches.languages.find(
        (lang: Language) => !item.value.values.map((val) => val.language_id
    ).includes(lang.code)) ?? arches.activeLanguage;

    return {
        id: maxOtherNewValueId + 1,
        valuetype_id: props.valueType ?? NOTE_CHOICES.scope,
        language_id: nextLanguage.code,
        value: '',
        item_id: item.value.id,
    };
});

const buttonLabel = computed(() => {
    switch (props.valueType) {
        case PREF_LABEL:
            return $gettext("Add Preferred Label");
        case ALT_LABEL:
            return $gettext("Add Alternate Label");
        default:
            return $gettext("Add Note");
    }
});
</script>

<template>
    <Button
        class="add-value"
        raised
        @click="item.values.push(newValue)"
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
