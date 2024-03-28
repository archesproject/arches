<script setup lang="ts">
import arches from "arches";
import { computed, provide, ref } from "vue";
import { useGettext } from "vue3-gettext";

import ProgressSpinner from "primevue/progressspinner";
import Splitter from "primevue/splitter";
import SplitterPanel from "primevue/splitterpanel";

import ControlledListSplash from "@/components/ControlledListManager/ControlledListSplash.vue";
import ItemEditor from "@/components/ControlledListManager/ItemEditor.vue";
import ListCharacteristics from "@/components/ControlledListManager/ListCharacteristics.vue";
import ListHeader from "@/components/ControlledListManager/ListHeader.vue";
import ListTree from "@/components/ControlledListManager/ListTree.vue";
import { displayedRowKey, selectedLanguageKey } from "@/components/ControlledListManager/const.ts";

import type { ControlledListItem, Selectable } from "@/types/ControlledListManager";
import type { Language } from "@/types/arches";
import type { Ref } from "@/types/Ref";

const lightGray = "#f4f4f4";
const { $gettext } = useGettext();

// Strings: $gettext() is a problem in templates given <SplitterPanel> rerendering
// https://github.com/archesproject/arches/pull/10569/files#r1496212837
const SELECT_A_LIST = $gettext("Select a list from the sidebar.");

const displayedRow: Ref<Selectable | null> = ref(null);
function setDisplayedRow(val: Selectable | null) {
    displayedRow.value = val;
}
provide(displayedRowKey, { displayedRow, setDisplayedRow });

const selectedLanguage: Ref<Language> = ref(
    (arches.languages as Language[]).find(l => l.code === arches.activeLanguage)
);
provide(selectedLanguageKey, selectedLanguage);

const listOrItemView = computed(() => {
    if (!displayedRow.value) {
        return ListCharacteristics;
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
                :style="{ margin: '1rem' }"
            >
                <component
                    :is="listOrItemView"
                    v-if="displayedRow"
                    :key="displayedRow.id"
                />
                <ControlledListSplash
                    v-else
                    :description="SELECT_A_LIST"
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
.p-splitter-panel {
    overflow-y: auto;
}
</style>
