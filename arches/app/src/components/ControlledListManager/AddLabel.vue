<script setup lang="ts">
import arches from "arches";
import { computed, ref } from "vue";
import { useGettext } from "vue3-gettext";

import EditLabel from "@/components/ControlledListManager/EditLabel.vue";

import type {
    ControlledListItem,
    Label,
    LanguageMap,
    ValueType,
} from "@/types/ControlledListManager";

const props: {
    item: ControlledListItem;
    languageMap: LanguageMap;
    type: ValueType;
    onInsert: (label: Label) => Promise<Label>;
} = defineProps(["item", "languageMap", "type", "onInsert"]);

const visible = ref(false);

const { $gettext } = useGettext();
const slateBlue = "#2d3c4b"; // todo: import from theme somewhere

const buttonLabel = computed(() => {
    return props.type === "prefLabel"
        ? $gettext("Add Preferred Label")
        : $gettext("Add Alternate Label");
});
</script>

<template>
    <button
        class="add-label"
        @click="visible = true"
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
        v-model="visible"
        :item
        :header="buttonLabel"
        :language-map
        :label="{
            id: null,
            valuetype: props.type,
            language: arches.activeLanguage,
            value: '',
        }"
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
