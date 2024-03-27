<script setup lang="ts">
import arches from "arches";
import { computed, inject, ref } from "vue";
import { useGettext } from "vue3-gettext";

import EditLabel from "@/components/ControlledListManager/EditLabel.vue";

import { itemKey, ALT_LABEL, PREF_LABEL } from "@/components/ControlledListManager/const.ts";

import type {
    NewLabel,
    ValueType,
} from "@/types/ControlledListManager";

const props: { type: ValueType } = defineProps(["type"]);
const { item } = inject(itemKey);

const modalVisible = ref(false);

const { $gettext } = useGettext();
const slateBlue = "#2d3c4b"; // todo: import from theme somewhere

const newLabel: NewLabel = computed(() => {
    return {
        id: null,
        valuetype: props.type,
        language: arches.activeLanguage,
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
    <button
        class="add-label"
        @click="modalVisible = true"
    >
        <i
            class="fa fa-plus-circle"
            aria-hidden="true"
        />
        <span class="add-label-text">
            {{ buttonLabel }}
        </span>
    </button>
    <EditLabel
        v-model="modalVisible"
        :header="buttonLabel"
        :label="newLabel"
        :is-insert="true"
    />
</template>

<style scoped>
.add-label {
    display: flex;
    width: 100%;
    height: 4rem;
    color: v-bind(slateBlue);
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
