<script setup lang="ts">
import { inject } from "vue";
import { useGettext } from "vue3-gettext";

import { itemKey, selectedLanguageKey } from "@/controlled-lists/constants.ts";
import { bestLabel } from "@/controlled-lists/utils.ts";
import LetterCircle from "@/controlled-lists/components/misc/LetterCircle.vue";

import type { Ref } from "vue";
import type { Language } from "@/arches/types";
import type { ControlledListItem } from "@/controlled-lists/types";

const selectedLanguage = inject(selectedLanguageKey) as Ref<Language>;
const item = inject(itemKey) as Ref<ControlledListItem>;

const { $gettext } = useGettext();

const iconLabel = (item: ControlledListItem) => {
    return item.guide ? $gettext("Guide Item") : $gettext("Indexable Item");
};
</script>

<template>
    <span class="item-header">
        <LetterCircle :labelled="item" />
        <h3>{{ bestLabel(item, selectedLanguage.code).value }}</h3>
        <span class="item-type">{{ iconLabel(item) }}</span>
        <a
            v-if="item.uri"
            :href="item.uri"
            rel="noreferrer"
            target="_blank"
            style="font-size: small; color: blue"
        >
            {{ item.uri }}
        </a>
    </span>
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
    font-size: 1.6rem;
    margin: 0;
}

.item-type {
    font-size: small;
    font-weight: 200;
}
</style>
