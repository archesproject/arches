<script setup lang="ts">
import { computed, inject } from "vue";

import ProgressSpinner from "primevue/progressspinner";
import Splitter from "primevue/splitter";
import SplitterPanel from "primevue/splitterpanel";

import { displayedRowKey, routes } from "@/arches_references/constants.ts";
import { dataIsList } from "@/arches_references/utils.ts";
import ControlledListSplash from "@/arches_references/components/misc/ControlledListSplash.vue";
import ItemEditor from "@/arches_references/components/editor/ItemEditor.vue";
import ListCharacteristics from "@/arches_references/components/editor/ListCharacteristics.vue";
import ListTree from "@/arches_references/components/tree/ListTree.vue";

import type { Ref } from "vue";
import type { ControlledList } from "@/arches_references/types";

const { displayedRow } = inject(displayedRowKey) as unknown as {
    displayedRow: Ref<ControlledList>;
};

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
</template>
