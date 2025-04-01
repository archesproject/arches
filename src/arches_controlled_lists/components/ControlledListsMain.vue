<script setup lang="ts">
import arches from "arches";
import { provide, ref } from "vue";
import { useRouter } from "vue-router";

import ConfirmDialog from "primevue/confirmdialog";
import Toast from "primevue/toast";

import {
    ENGLISH,
    displayedRowKey,
    selectedLanguageKey,
    systemLanguageKey,
} from "@/arches_controlled_lists/constants.ts";
import { routeNames } from "@/arches_controlled_lists/routes.ts";
import { dataIsList } from "@/arches_controlled_lists/utils.ts";

import ListHeader from "@/arches_controlled_lists/components/misc/ListHeader.vue";
import MainSplitter from "@/arches_controlled_lists/components/MainSplitter.vue";

import type { Ref } from "vue";
import type { Language } from "@/arches_vue_utils/types";
import type { Selectable } from "@/arches_controlled_lists/types";

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
const systemLanguage = ENGLISH; // TODO: get from settings
provide(systemLanguageKey, systemLanguage);
</script>

<template>
    <div style="height: 100vh; padding-bottom: 2.5rem">
        <div class="list-editor-container">
            <ListHeader />
            <MainSplitter />
        </div>
    </div>
    <Toast
        :pt="{
            messageIcon: {
                style: { marginTop: 'var(--p-toast-text-gap)' },
            },
        }"
    />
    <ConfirmDialog
        :draggable="false"
        :pt="{
            header: {
                style: {
                    background: 'var(--p-navigation-header-color)',
                    color: 'white',
                    borderRadius: '1rem',
                    marginBottom: '1rem',
                },
            },
            title: {
                style: {
                    fontWeight: 800,
                    fontSize: 'small',
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
