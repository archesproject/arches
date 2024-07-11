<script setup lang="ts">
import arches from "arches";
import { computed, provide, ref } from "vue";
import { useRouter } from "vue-router";

import ConfirmDialog from "primevue/confirmdialog";
import ProgressSpinner from "primevue/progressspinner";
import Splitter from "primevue/splitter";
import SplitterPanel from "primevue/splitterpanel";
import Toast from "primevue/toast";

import { LIGHT_GRAY } from "@/arches/theme.ts";
import {
    displayedRowKey,
    routes,
    selectedLanguageKey,
} from "@/controlled-lists/constants.ts";
import { dataIsList } from "@/controlled-lists/utils.ts";
import ControlledListSplash from "@/controlled-lists/components/misc/ControlledListSplash.vue";
import ItemEditor from "@/controlled-lists/components/editor/ItemEditor.vue";
import ListCharacteristics from "@/controlled-lists/components/editor/ListCharacteristics.vue";
import ListHeader from "@/controlled-lists/components/misc/ListHeader.vue";
import ListTree from "@/controlled-lists/components/tree/ListTree.vue";

import type { Ref } from "vue";
import type { ControlledListItem, Selectable } from "@/controlled-lists/types";
import type { Language } from "@/arches/types";

const router = useRouter();

const displayedRow: Ref<Selectable | null> = ref(null);
function setDisplayedRow(row: Selectable | null) {
    displayedRow.value = row;
    if (row === null) {
        router.push({ name: routes.splash });
        return;
    }
    if (typeof row.id === "number") {
        return;
    }
    if ((row as ControlledListItem).controlled_list_id) {
        router.push({ name: routes.item, params: { id: row.id } });
    } else {
        router.push({ name: routes.list, params: { id: row.id } });
    }
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
    <!-- Subtract size of arches toolbars -->
    <div style="width: calc(100vw - 50px); height: calc(100vh - 50px)">
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
                        :key="displayedRow?.id ?? routes.splash"
                    />
                </SplitterPanel>
            </Splitter>
        </div>
    </div>
    <Toast />
    <ConfirmDialog :draggable="false" />
</template>

<style scoped>
.list-editor-container {
    display: flex;
    flex-direction: column;
    height: 100%;
}
</style>
