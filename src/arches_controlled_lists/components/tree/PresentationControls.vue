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
} from "@/arches_controlled_lists/constants.ts";
import { shouldUseContrast } from "@/arches_controlled_lists/utils.ts";

import type { Ref } from "vue";
import type { Language } from "@/arches_vue_utils/types";

const { expandAll, collapseAll } = defineProps<{
    expandAll: () => void;
    collapseAll: () => void;
}>();

let selectedLanguage: Ref<Language> | undefined;
if (arches.languages) {
    // arches-lingo reuses this component without this provided.
    selectedLanguage = inject(selectedLanguageKey);
}

const { $gettext } = useGettext();
</script>

<template>
    <div class="tree-controls-container">
        <div class="container-title">
            Tree controls
        </div>
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
            <div
                v-if="arches.languages"
                class="language-select"
            >
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
    </div>
</template>

<style scoped>
.tree-controls-container {
    padding: 0 0 .5rem 0;
    background: #fafafa;
    border-bottom: 1px solid #ddd;
}

.container-title {
    padding: 0.75rem 0 0 1.25rem;
}

.secondary-button {
    height: 3rem;
    margin: 0.5rem;
    font-size: smaller;
}

.language-select {
    display: flex;
    flex-grow: 1;
    justify-content: flex-end;
}
</style>
