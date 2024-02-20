<script setup lang="ts">
import { computed } from "vue";
import { useGettext } from "vue3-gettext";

import { useToast } from "primevue/usetoast";

import { deleteLabel } from "@/components/ControlledListManager/api.ts";
import AddLabel from "@/components/ControlledListManager/AddLabel.vue";
import LabelRow from "@/components/ControlledListManager/LabelRow.vue";

import type {
    ControlledListItem,
    Label,
    LanguageMap,
    ValueType,
} from "@/types/ControlledListManager";

const props: {
    item: ControlledListItem;
    languageMap: LanguageMap;
    type: ValueType | "URI";
} = defineProps(["item", "languageMap", "type"]);

const onInsert = (label: Label) => {
    // eslint-disable-next-line vue/no-mutating-props
    props.item.labels.push(label);
};

const toast = useToast();
const { $gettext } = useGettext();
const slateBlue = "#2d3c4b"; // todo: import from theme somewhere

const headings: { heading: string; subheading: string } = computed(() => {
    switch (props.type) {
        case "prefLabel":
            return {
                heading: $gettext("Preferred Label(s)"),
                subheading: $gettext(
                    "Provide at least one preferred label and language for your list item."
                ),
            };
        case "altLabel":
            return {
                heading: $gettext("Alternate Label(s)"),
                subheading: $gettext(
                    "Optionally, you can provide additional label/language labels for your list item. Useful if you want to make searching for labels with synonyms or common misspellings of your preferred label(s) easier."
                ),
            };
        case "URI":
            return {
                heading: $gettext("List Item URI"),
                subheading: $gettext(
                    "Optionally, provide a URI for your list item. Useful if your list item is formally defined in a thesaurus or authority document."
                ),
            };
        default:
            return {
                heading: "",
                subheading: "",
            };
    }  
});

const onDelete = async (label: Label) => {
    await deleteLabel(label, toast, $gettext);
    const toDelete = props.item.labels.findIndex(l => l.id === label.id);
    // eslint-disable-next-line vue/no-mutating-props
    props.item.labels.splice(toDelete, 1);
};
</script>

<template>
    <div class="label-editor-container">
        <h4>{{ headings.heading }}</h4>
        <h5>{{ headings.subheading }}</h5>
        <div
            v-for="label in item.labels.filter(
                label => label.valuetype === props.type
            )"
            :key="label.id"
            class="label-box"
        >
            <LabelRow
                :label
                :language-map
                :on-delete="() => { onDelete(label) }"
            />
        </div>
        <AddLabel
            v-if="type !== 'URI'"
            :item
            :language-map
            :type="type"
            :on-insert
        />
    </div>
</template>

<style scoped>
.label-editor-container {
    margin: 1rem 1rem 3rem 1rem;
    width: 80%;
}
h4 {
    color: v-bind(slateBlue);
    margin-top: 0;
    font-size: small;
}
h5 {
    font-weight: normal;
    margin-top: 0;
}
</style>
