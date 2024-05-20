<script setup lang="ts">
import arches from "arches";
import { computed, inject } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";

import { ARCHES_CHROME_BLUE } from "@/theme.ts";
import { itemKey, ALT_LABEL, PREF_LABEL } from "@/components/ControlledListManager/constants.ts";

import type { Ref } from "vue";
import type {
    ControlledListItem,
    Label,
    NewLabel,
    ValueType,
} from "@/types/ControlledListManager";

const props = defineProps<{ type: ValueType }>();
const item = inject(itemKey) as Ref<ControlledListItem>;

const { $gettext } = useGettext();

const newLabel: Ref<NewLabel> = computed(() => {
    const otherNewLabelIds = item.value.labels.filter(
        (label: NewLabel | Label) => typeof label.id === "number"
    ).map(label => label.id as unknown as number);
    const maxOtherNewLabelId = Math.max(
        ...otherNewLabelIds,
        1000,
    );
    return {
        id: maxOtherNewLabelId + 1,
        valuetype_id: props.type,
        language_id: arches.activeLanguage,
        value: '',
        item_id: item.value.id,
    };
});

const buttonLabel = computed(() => {
    switch (props.type) {
        case PREF_LABEL:
            return $gettext("Add Preferred Label");
        case ALT_LABEL:
            return $gettext("Add Alternate Label");
        default:
            throw new Error();
    }
});
</script>

<template>
    <Button
        class="add-label"
        raised
        @click="item.labels.push(newLabel)"
    >
        <i
            class="fa fa-plus-circle"
            aria-hidden="true"
        />
        <span class="add-label-text">
            {{ buttonLabel }}
        </span>
    </Button>
</template>

<style scoped>
.add-label {
    display: flex;
    height: 3rem;
    color: v-bind(ARCHES_CHROME_BLUE);
    background-color: #f3fbfd;
    margin-top: 1rem;
}
.add-label > i,
.add-label > span {
    align-self: center;
}
.add-label-text {
    margin: 1rem;
    font-size: small;
    font-weight: 600;
}
</style>
