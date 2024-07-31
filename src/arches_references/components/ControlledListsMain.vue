<script setup lang="ts">
import arches from "arches";
import { computed, provide, ref } from "vue";
import { useRouter } from "vue-router";

import ConfirmDialog from "primevue/confirmdialog";
import ProgressSpinner from "primevue/progressspinner";
import Splitter from "primevue/splitter";
import SplitterPanel from "primevue/splitterpanel";
import Toast from "primevue/toast";

import {
    displayedRowKey,
    routes,
    selectedLanguageKey,
} from "@/arches_references/constants.ts";
import { dataIsList } from "@/arches_references/utils.ts";
import ControlledListSplash from "@/arches_references/components/misc/ControlledListSplash.vue";
import ItemEditor from "@/arches_references/components/editor/ItemEditor.vue";
import ListCharacteristics from "@/arches_references/components/editor/ListCharacteristics.vue";
import ListHeader from "@/arches_references/components/misc/ListHeader.vue";
import ListTree from "@/arches_references/components/tree/ListTree.vue";

import type { Ref } from "vue";
import type { Language } from "@/arches/types";
import type { Selectable } from "@/arches_references/types";

const router = useRouter();

const displayedRow: Ref<Selectable | null> = ref(null);
const setDisplayedRow = (val: Selectable | null) => {
    displayedRow.value = val;
    if (val === null) {
        router.push({ name: routes.splash });
        return;
    }
    if (typeof val.id === "number") {
        return;
    }
    if (dataIsList(val)) {
        router.push({ name: routes.list, params: { id: val.id } });
    } else {
        router.push({ name: routes.item, params: { id: val.id } });
    }
};
// @ts-expect-error vue-tsc doesn't like arbitrary properties here
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
            <Splitter style="height: 100%">
                <SplitterPanel
                    :size="34"
                    :min-size="25"
                    style="display: flex; flex-direction: column"
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
    <ConfirmDialog
        :draggable="false"
        :pt="{
            root: {
                style: {
                    fontSize: 'small',
                },
            },
            header: {
                style: {
                    background: 'var(--p-navigation)',
                    color: 'white',
                    borderRadius: '1rem',
                    marginBottom: '1rem',
                },
            },
            title: {
                style: {
                    fontWeight: 800,
                },
            },
        }"
    />
</template>

<style scoped>
.list-editor-container {
    display: flex;
    flex-direction: column;
    height: 100%;
}
</style>
