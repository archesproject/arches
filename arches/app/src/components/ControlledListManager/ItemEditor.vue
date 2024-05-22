<script setup lang="ts">
import { inject, provide } from "vue";
import { useGettext } from "vue3-gettext";

import ItemImages from "@/components/ControlledListManager/ItemImages.vue";
import ItemURI from "@/components/ControlledListManager/ItemURI.vue";
import LabelEditor from "@/components/ControlledListManager/LabelEditor.vue";
import LetterCircle from "@/components/ControlledListManager/LetterCircle.vue";

import {
    displayedRowKey,
    itemKey,
    selectedLanguageKey,
    ALT_LABEL,
    PREF_LABEL,
} from "@/components/ControlledListManager/constants.ts";
import { bestLabel } from "@/components/ControlledListManager/utils.ts";

import type { Ref } from "vue";
import type { Language } from "@/types/arches";
import type {
    ControlledListItem,
    DisplayedListItemRefAndSetter,
} from "@/types/ControlledListManager";

const { displayedRow: item } = inject(displayedRowKey) as DisplayedListItemRefAndSetter;
const selectedLanguage = inject(selectedLanguageKey) as Ref<Language>;

const { $gettext } = useGettext();

provide(itemKey, item);

const iconLabel = (item: ControlledListItem) => {
    return item.guide ? $gettext("Guide Item") : $gettext("Indexable Item");
};
</script>

<template>
    <template v-if="item">
        <span class="item-header">
            <LetterCircle :labelled="item" />
            <h3>{{ bestLabel(item, selectedLanguage.code).value }}</h3>
            <span class="item-type">{{ iconLabel(item) }}</span>
            <a
                v-if="item.uri"
                :href="item.uri"
                rel="noreferrer"
                target="_blank"
                style="font-size: small; color: blue;"
            >
                {{ item.uri }}
            </a>
        </span>
        <LabelEditor :value-type="PREF_LABEL" />
        <LabelEditor :value-type="ALT_LABEL" />
        <div class="field-editor-container">
            <ItemURI />
        </div>
        <div class="field-editor-container images-container">
            <ItemImages />
        </div>
    </template>
</template>

<style scoped>
.item-header {
    display: inline-flex;
    align-items: center;
    gap: 1rem;
    margin: 1rem 1rem 0rem 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid;
    width: 100%;
}

h3 {
    font-size: 1.5rem;
    margin: 0;
}

.item-type {
    font-size: small;
    font-weight: 200;
}

.field-editor-container {
    margin: 1rem 1rem 3rem 1rem;
    display: flex;
    flex-direction: column;
    width: 100%;
}

.images-container {
    gap: 20px;
}
</style>
