<script setup lang="ts">
import { inject } from "vue";

import ProgressSpinner from "primevue/progressspinner";
import Splitter from "primevue/splitter";
import SplitterPanel from "primevue/splitterpanel";

import { displayedRowKey } from "@/arches_controlled_lists/constants.ts";
import { dataIsList } from "@/arches_controlled_lists/utils.ts";
import ControlledListSplash from "@/arches_controlled_lists/components/misc/ControlledListSplash.vue";
import ItemEditor from "@/arches_controlled_lists/components/editor/ItemEditor.vue";
import ListEditor from "@/arches_controlled_lists/components/editor/ListEditor.vue";
import ListTree from "@/arches_controlled_lists/components/tree/ListTree.vue";

import type { Ref } from "vue";
import type { ControlledList } from "@/arches_controlled_lists/types";

const { displayedRow } = inject<{ displayedRow: Ref<ControlledList> }>(
    displayedRowKey,
)!;
</script>

<template>
    <Splitter>
        <SplitterPanel
            :size="30"
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
            :size="70"
            :min-size="25"
            :style="{
                margin: '1rem 0rem 4rem 1rem',
                overflowY: 'auto',
                paddingRight: '2rem',
            }"
        >
            <ControlledListSplash v-if="!displayedRow" />
            <ListEditor v-else-if="dataIsList(displayedRow)" />
            <ItemEditor v-else />
        </SplitterPanel>
    </Splitter>
</template>

<style scoped>
.p-splitter {
    height: 100%;
    overflow: hidden;
    border-radius: 0;
}
</style>
