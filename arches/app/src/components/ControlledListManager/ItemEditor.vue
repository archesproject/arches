<script setup lang="ts">
import { computed, inject, provide } from "vue";
import { useGettext } from "vue3-gettext";

import ItemCharacteristic from "@/components/ControlledListManager/ItemCharacteristic.vue";
import LabelEditor from "@/components/ControlledListManager/LabelEditor.vue";
import LetterCircle from "@/components/ControlledListManager/LetterCircle.vue";

import {
    displayedRowKey,
    itemKey,
    selectedLanguageKey,
    ALT_LABEL,
    PREF_LABEL,
} from "@/components/ControlledListManager/const.ts";
import { bestLabel } from "@/components/ControlledListManager/utils.ts";

import type { ControlledListItem, Label, NewLabel } from "@/types/ControlledListManager";

const { displayedRow: item } = inject(displayedRowKey);
const selectedLanguage = inject(selectedLanguageKey);

const { $gettext } = useGettext();
const slateBlue = "#2d3c4b"; // todo: import from theme somewhere

const appendItemLabel = computed(() => {
    return (newLabel: Label | NewLabel) => { item.value.labels.push(newLabel); };
});
const removeItemLabel = computed(() => {
    return (removedLabel: Label | NewLabel) => {
        const toDelete = item.value.labels.findIndex((l: Label) => l.id === removedLabel.id);
        item.value.labels.splice(toDelete, 1);
    };
});
const updateItemLabel = computed(() => {
    return (updatedLabel: Label) => {
        const toUpdate = item.value.labels.find((l: Label) => l.id === updatedLabel.id);
        toUpdate.language = updatedLabel.language;
        toUpdate.value = updatedLabel.value;
    };
});

provide(itemKey, { item });

const iconLabel = (item: ControlledListItem) => {
    return item.guide ? $gettext("Guide Item") : $gettext("Indexable Item");
};
</script>

<template>
    <span class="item-header">
        <LetterCircle
            v-if="item"
            :labelled="item"
        />
        <h3>{{ bestLabel(item, selectedLanguage.code).value }}</h3>
        <span class="item-type">{{ iconLabel(item) }}</span>
    </span>
    <LabelEditor
        :type="PREF_LABEL"
        :item
        :append-item-label
        :remove-item-label
        :update-item-label
    />
    <LabelEditor
        :type="ALT_LABEL"
        :item
        :append-item-label
        :remove-item-label
        :update-item-label
    />
    <div class="uri-editor-container">
        <h4>{{ $gettext("List Item URI") }}</h4>
        <p>
            {{ $gettext(
                "Optionally, provide a URI for your list item. Useful if your list item is formally defined in a thesaurus or authority document."
            ) }}
        </p>
    </div>
    <ItemCharacteristic
        :editable="true"
        field="uri"
        :style="{ display: 'flex', alignItems: 'center', width: '80%' }"
    />
</template>

<style scoped>
.item-header {
    display: inline-flex;
    align-items: center;
    gap: 1rem;
    margin: 1rem 1rem 0rem 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid;
    width: 80%;
}

h3 {
    font-size: 1.5rem;
    margin: 0;
}

h4 {
    color: v-bind(slateBlue);
    margin-top: 0;
    font-size: small;
}

p {
    font-weight: normal;
    margin-top: 0;
    font-size: small;
}

.item-type {
    font-size: small;
    font-weight: 200;
}

.uri-editor-container {
    margin: 1rem 1rem 3rem 1rem;
    width: 80%;
}
</style>
