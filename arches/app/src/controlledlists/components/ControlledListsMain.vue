<script setup lang="ts">
import arches from "arches";
import { computed, provide, ref } from "vue";

import ProgressSpinner from "primevue/progressspinner";
import Splitter from "primevue/splitter";
import SplitterPanel from "primevue/splitterpanel";

import { LIGHT_GRAY } from "@/arches/theme.ts";
import {
    displayedRowKey,
    selectedLanguageKey,
} from "@/controlledlists/constants.ts";
import { dataIsList } from "@/controlledlists/utils.ts";
import ControlledListSplash from "@/controlledlists/components/misc/ControlledListSplash.vue";
import ItemEditor from "@/controlledlists/components/editor/ItemEditor.vue";
import ListCharacteristics from "@/controlledlists/components/editor/ListCharacteristics.vue";
import ListHeader from "@/controlledlists/components/misc/ListHeader.vue";
import ListTree from "@/controlledlists/components/tree/ListTree.vue";

import type { Ref } from "vue";
import type { Language } from "@/arches/types";
import type { Selectable } from "@/controlledlists/types";

const splash = "splash";

const displayedRow: Ref<Selectable | null> = ref(null);
function setDisplayedRow(val: Selectable | null) {
    displayedRow.value = val;
}
provide(displayedRowKey, { displayedRow, setDisplayedRow });

const selectedLanguage: Ref<Language> = ref(
    (arches.languages as Language[]).find(
        (lang) => lang.code === arches.activeLanguage,
    ) as Language,
);
provide(selectedLanguageKey, selectedLanguage);

const panel = computed(() => {
    if (!displayedRow.value) {
        return ControlledListSplash;
    }
    if (dataIsList(displayedRow.value)) {
        return ListCharacteristics;
    }
    return ItemEditor;
});
</script>

<template>
    <div class="list-editor-container">
        <ListHeader />
        <Splitter
            :pt="{
                root: { style: { height: '100%' } },
                gutter: { style: { background: LIGHT_GRAY } },
                gutterHandler: { style: { background: LIGHT_GRAY } },
            }"
        >
            <SplitterPanel
                :size="34"
                :min-size="25"
                :pt="{
                    root: {
                        style: { display: 'flex', flexDirection: 'column' },
                    },
                }"
            >
                <Suspense>
                    <ListTree />
                    <template #fallback>
                        <ProgressSpinner />
                    </template>
                </Suspense>
            </SplitterPanel>
            <SplitterPanel
                :size="66"
                :min-size="25"
                :style="{
                    margin: '1rem 0rem 4rem 1rem',
                    overflowY: 'auto',
                    paddingRight: '4rem',
                }"
            >
                <component
                    :is="panel"
                    :key="displayedRow?.id ?? splash"
                />
            </SplitterPanel>
        </Splitter>
    </div>
</template>

<style scoped>
.list-editor-container {
    display: flex;
    flex-direction: column;
    height: 100%;
}
</style>
