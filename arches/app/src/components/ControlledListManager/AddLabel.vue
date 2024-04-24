<script setup lang="ts">
import arches from "arches";
import { computed, inject } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";

import { itemKey, ALT_LABEL, PREF_LABEL } from "@/components/ControlledListManager/const.ts";

import type {
    Label,
    NewLabel,
    ValueType,
} from "@/types/ControlledListManager";

const props: { type: ValueType } = defineProps(["type"]);
const { item } = inject(itemKey);

const { $gettext } = useGettext();
const slateBlue = "#2d3c4b"; // todo: import from theme somewhere

const newLabel: NewLabel = computed(() => {
    const otherNewLabels = item.value.labels.filter(
        (l: NewLabel | Label) => typeof l.id === "number"
    // eslint-disable-next-line @typescript-eslint/no-explicit-any 
    ) as any as NewLabel[];
    const maxOtherNewLabelId = Math.max(
        ...otherNewLabels.map(l => l.id),
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
    color: v-bind(slateBlue);
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
