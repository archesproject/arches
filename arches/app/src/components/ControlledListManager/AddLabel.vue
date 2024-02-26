<script setup lang="ts">
import arches from "arches";
import { computed, ref } from "vue";
import { useGettext } from "vue3-gettext";

import EditLabel from "@/components/ControlledListManager/EditLabel.vue";

import type {
    ControlledListItem,
    Label,
    NewLabel,
    ValueType,
} from "@/types/ControlledListManager";

const props: {
    item: ControlledListItem;
    type: ValueType;
    onInsert: (label: Label) => Promise<Label>;
} = defineProps(["item", "type", "onInsert"]);

const modalVisible = ref(false);

const { $gettext } = useGettext();
const slateBlue = "#2d3c4b"; // todo: import from theme somewhere

const newLabel: NewLabel = computed(() => {
    return {
        id: null,
        valuetype: props.type,
        language: arches.activeLanguage,
        value: '',
        item_id: props.item.id,
    };
});

const buttonLabel = computed(() => {
    switch (props.type) {
        case "prefLabel":
            return $gettext("Add Preferred Label");
        case "altLabel":
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
        :on-insert
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
