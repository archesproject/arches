<script setup lang="ts">
import arches from "arches";
import { inject } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import Select from "primevue/select";

import {
    CONTRAST,
    SECONDARY,
    selectedLanguageKey,
} from "@/arches_references/constants.ts";
import { shouldUseContrast } from "@/arches_references/utils.ts";

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
            :severity="shouldUseContrast() ? CONTRAST : SECONDARY"
            class="secondary-button"
            type="button"
            icon="fa fa-plus"
            :label="$gettext('Expand all')"
            @click="expandAll"
        />
        <Button
            :severity="shouldUseContrast() ? CONTRAST : SECONDARY"
            class="secondary-button"
            type="button"
            icon="fa fa-minus"
            :label="$gettext('Collapse all')"
            @click="collapseAll"
        />
        <div style="display: flex; flex-grow: 1; justify-content: flex-end">
            <span
                id="languageSelectLabel"
                style="
                    align-self: center;
                    margin-right: 0.25rem;
                    font-size: smaller;
                "
            >
                {{ $gettext("Show labels in:") }}
            </span>
            <Select
                v-model="selectedLanguage"
                aria-labelledby="languageSelectLabel"
                :options="arches.languages"
                :option-label="
                    (lang: Language) => `${lang.name} (${lang.code})`
                "
                :placeholder="$gettext('Language')"
                :pt="{
                    root: { class: 'secondary-button' },
                    label: { style: { alignSelf: 'center' } },
                    optionLabel: { style: { fontSize: 'small' } },
                }"
            />
        </div>
    </div>
</template>

<style scoped>
.secondary-button {
    height: 3rem;
    margin: 0.5rem;
}
</style>
