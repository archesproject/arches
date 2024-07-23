<script setup lang="ts">
import arches from "arches";
import { inject } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import Dropdown from "primevue/dropdown";

import { selectedLanguageKey } from "@/controlled-lists/constants.ts";

import type { Ref } from "vue";
import type { Language } from "@/arches/types";

const { $gettext } = useGettext();

const selectedLanguage = inject(selectedLanguageKey) as Ref<Language>;

const { expandAll, collapseAll } = defineProps<{
    expandAll: () => void;
    collapseAll: () => void;
}>();
</script>

<template>
    <div style="text-align: center; display: flex; width: 100%">
        <Button
            class="secondary-button"
            type="button"
            icon="fa fa-plus"
            :label="$gettext('Expand all')"
            @click="expandAll"
        />
        <Button
            class="secondary-button"
            type="button"
            icon="fa fa-minus"
            :label="$gettext('Collapse all')"
            @click="collapseAll"
        />
        <div style="display: flex; flex-grow: 1; justify-content: flex-end">
            <span
                id="languageSelectLabel"
                style="align-self: center; margin-right: 0.25rem"
            >
                {{ $gettext("Show labels in:") }}
            </span>
            <Dropdown
                v-model="selectedLanguage"
                aria-labelledby="languageSelectLabel"
                :options="arches.languages"
                :option-label="(lang) => `${lang.name} (${lang.code})`"
                :placeholder="$gettext('Language')"
                :pt="{
                    root: { class: 'p-button secondary-button' },
                    input: {
                        style: {
                            fontFamily: 'inherit',
                            fontSize: 'small',
                            textAlign: 'center',
                            alignContent: 'center',
                        },
                    },
                    itemLabel: { style: { fontSize: 'small' } },
                }"
            />
        </div>
    </div>
</template>

<style scoped>
.secondary-button {
    border: 0;
    background: #f4f4f4;
    height: 3rem;
    margin: 0.5rem;
    justify-content: center;
    font-weight: 600;
    text-wrap: nowrap;
}
</style>
