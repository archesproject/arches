<script setup lang="ts">
import arches from "arches";
import { provide, ref } from "vue";
import { useRouter } from "vue-router";

import ConfirmDialog from "primevue/confirmdialog";
import Toast from "primevue/toast";

import {
    displayedRowKey,
    selectedLanguageKey,
} from "@/arches_references/constants.ts";
import { routeNames } from "@/arches_references/routes.ts";
import { dataIsList } from "@/arches_references/utils.ts";

import ListHeader from "@/arches_references/components/misc/ListHeader.vue";
import MainSplitter from "@/arches_references/components/MainSplitter.vue";

import type { Ref } from "vue";
import type { Language } from "@/arches_vue_utils/types";
import type { Selectable } from "@/arches_references/types";

const router = useRouter();

const displayedRow: Ref<Selectable | null> = ref(null);
const setDisplayedRow = (val: Selectable | null) => {
    displayedRow.value = val;
    if (val === null) {
        router.push({ name: routeNames.splash });
        return;
    }
    if (typeof val.id === "number") {
        return;
    }
    if (dataIsList(val)) {
        router.push({ name: routeNames.list, params: { id: val.id } });
    } else {
        router.push({ name: routeNames.item, params: { id: val.id } });
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
</script>

<template>
    <!-- Subtract size of arches toolbars -->
    <div style="width: calc(100vw - 50px); height: calc(100vh - 50px)">
        <div class="list-editor-container">
            <ListHeader />
            <MainSplitter />
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

:deep(h2) {
    font-size: medium;
}

:deep(h3) {
    font-size: medium;
}

:deep(h4) {
    font-size: small;
}
</style>
