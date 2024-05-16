<script setup lang="ts">
import arches from "arches";
import { computed, provide, ref } from "vue";

import ProgressSpinner from "primevue/progressspinner";
import Splitter from "primevue/splitter";
import SplitterPanel from "primevue/splitterpanel";

import ControlledListSplash from "@/components/ControlledListManager/ControlledListSplash.vue";
import ItemEditor from "@/components/ControlledListManager/ItemEditor.vue";
import ListCharacteristics from "@/components/ControlledListManager/ListCharacteristics.vue";
import ListHeader from "@/components/ControlledListManager/ListHeader.vue";
import ListTree from "@/components/ControlledListManager/ListTree.vue";
import { displayedRowKey, selectedLanguageKey } from "@/components/ControlledListManager/const.ts";

import type { Ref } from "vue";
import type { ControlledListItem, Selectable } from "@/types/ControlledListManager";
import type { Language } from "@/types/arches";

const lightGray = "#f4f4f4";

const displayedRow: Ref<Selectable | null> = ref(null);
function setDisplayedRow(val: Selectable | null) {
    displayedRow.value = val;
}
provide(displayedRowKey, { displayedRow, setDisplayedRow });

const selectedLanguage: Ref<Language> = ref(
    (arches.languages as Language[]).find(l => l.code === arches.activeLanguage) as Language
);
provide(selectedLanguageKey, selectedLanguage);

const panel = computed(() => {
    if (!displayedRow.value) {
        return ControlledListSplash;
    }
    if ((displayedRow.value as ControlledListItem).depth === undefined) {
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
                root: { style: { height: '97%' } },
                gutter: { style: { background: lightGray } },
                gutterHandler: { style: { background: lightGray } },
            }"
        >
            <SplitterPanel
                :size="40"
                :min-size="25"
                :pt="{
                    root: { style: { display: 'flex', flexDirection: 'column' } },
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
                :size="60"
                :min-size="25"
                :style="{ margin: '1rem 0rem 1rem 1rem', overflowY: 'auto', maxWidth: '1200px', paddingRight: '7%' }"
            >
                <component
                    :is="panel"
                    :key="displayedRow?.id ?? 'splash'"
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
