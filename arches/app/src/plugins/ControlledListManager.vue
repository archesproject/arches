<script setup lang="ts">
import { ref, provide } from "vue";
import { useGettext } from "vue3-gettext";

import ProgressSpinner from "primevue/progressspinner";
import Splitter from "primevue/splitter";
import SplitterPanel from "primevue/splitterpanel";
import Toast from "primevue/toast";

import ControlledListEditor from "@/components/ControlledListManager/ControlledListEditor.vue";
import ControlledListSplash from "@/components/ControlledListManager/ControlledListSplash.vue";
import SidepanelDataView from "@/components/ControlledListManager/SidepanelDataView.vue";
import { displayedListKey } from "@/components/ControlledListManager/const.ts";

import type { Ref } from "@/types/Ref";
import type { ControlledList } from "@/types/ControlledListManager";

const displayedList: Ref<ControlledList | null> = ref(null);

function setDisplayedList(val: ControlledList | null) {
    displayedList.value = val;
}

provide(displayedListKey, { displayedList, setDisplayedList });

const { $gettext } = useGettext();
const lightGray = "#f4f4f4";
const CONTROLLED_LISTS = $gettext("Controlled Lists");
const SELECT_A_LIST = $gettext("Select a list from the sidebar.");
</script>

<template>
    <!-- Subtract size of arches toolbars -->
    <div style="width: calc(100vw - 50px); height: calc(100vh - 50px)">
        <div style="height: 100%">
            <Splitter
                :pt="{
                    gutter: { style: { background: lightGray } },
                    gutterHandler: { style: { background: lightGray } },
                }"
            >
                <SplitterPanel
                    :size="30"
                    :min-size="15"
                >
                    <div class="header">
                        <h2>{{ CONTROLLED_LISTS }}</h2>
                    </div>

                    <Suspense>
                        <SidepanelDataView />
                        <template #fallback>
                            <ProgressSpinner />
                        </template>
                    </Suspense>
                </SplitterPanel>

                <SplitterPanel
                    :size="70"
                    :min-size="50"
                    class="mt-0"
                >
                    <ControlledListEditor
                        v-if="displayedList"
                        :key="displayedList.id"
                        :displayed-list
                    />
                    <ControlledListSplash
                        v-else
                        :description="SELECT_A_LIST"
                    />
                </SplitterPanel>
            </Splitter>
        </div>
    </div>
    <Toast />
</template>

<!-- Not scoped: workaround for lack of font-family in <body> -->
<style>
div {
    font-family: "Open Sans";
}
</style>

<style scoped>
.header {
    background: #f4f4f4;
    display: flex;
    align-items: center;
}
h2 {
    font-size: 1.5rem;
    margin: 1rem;
}
.p-splitter {
    background: white;
    font-size: 14px;
    border: 0;
    height: 100%;
}
.p-splitter-panel {
    display: flex;
    flex-direction: column;
}
</style>