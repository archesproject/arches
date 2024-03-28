<script setup lang="ts">
import { computed, inject, provide } from "vue";
import { useGettext } from "vue3-gettext";

import ItemCharacteristic from "@/components/ControlledListManager/ItemCharacteristic.vue";
import LabelEditor from "@/components/ControlledListManager/LabelEditor.vue";
import LetterCircle from "@/components/ControlledListManager/LetterCircle.vue";

import { displayedRowKey, selectedLanguageKey, ALT_LABEL, PREF_LABEL, URI } from "@/components/ControlledListManager/const.ts";
import { itemKey } from "@/components/ControlledListManager/const.ts";
import { bestLabel } from "@/components/ControlledListManager/utils.ts";

import type { ControlledListItem, Label } from "@/types/ControlledListManager";

const { displayedRow: item } = inject(displayedRowKey);
const selectedLanguage = inject(selectedLanguageKey);

const { $gettext } = useGettext();

const appendItemLabel = computed(() => {
    return (newLabel: Label) => { item.value.labels.push(newLabel); };
});
const removeItemLabel = computed(() => {
    return (removedLabel: Label) => {
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

provide(itemKey, { item, appendItemLabel, removeItemLabel, updateItemLabel });

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
    <LabelEditor :type="PREF_LABEL" />
    <LabelEditor :type="ALT_LABEL" />
    <LabelEditor
        :type="URI"
        :style="{ marginBottom: 0 }"
    />
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

.item-type {
    font-size: small;
    font-weight: 200;
}
</style>
