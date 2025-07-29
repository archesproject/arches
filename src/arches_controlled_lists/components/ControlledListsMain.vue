<script setup lang="ts">
import arches from "arches";
import { provide, ref } from "vue";
import { useGettext } from "vue3-gettext";
import { useRouter } from "vue-router";

import { useConfirm } from "primevue/useconfirm";
import ConfirmDialog from "primevue/confirmdialog";
import Toast from "primevue/toast";

import {
    CONTRAST,
    DANGER,
    SECONDARY,
    ENGLISH,
    displayedRowKey,
    isEditingKey,
    selectedLanguageKey,
    systemLanguageKey,
} from "@/arches_controlled_lists/constants.ts";
import { routeNames } from "@/arches_controlled_lists/routes.ts";
import {
    commandeerFocusFromDataTable,
    dataIsList,
    shouldUseContrast,
} from "@/arches_controlled_lists/utils.ts";

import ListHeader from "@/arches_controlled_lists/components/misc/ListHeader.vue";
import MainSplitter from "@/arches_controlled_lists/components/MainSplitter.vue";

import type { Ref } from "vue";
import type { Language, Selectable } from "@/arches_controlled_lists/types";

const router = useRouter();
const confirm = useConfirm();
const { $gettext } = useGettext();

const isEditing = ref(false);
const displayedRow: Ref<Selectable | null> = ref(null);
const lastFocusedElement = ref<HTMLElement | null>(null);

const setDisplayedRow = (val: Selectable | null) => {
    if (val && isEditing.value) {
        confirmLeave(val);
    } else {
        finishSettingDisplayedRow(val);
    }
};

function setIsEditing(val: boolean) {
    isEditing.value = val;
}

const finishSettingDisplayedRow = (val: Selectable | null) => {
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

const confirmLeave = (row: Selectable) => {
    confirm.require({
        message: $gettext(
            "You have unsaved changes. Are you sure you want to leave?",
        ),
        header: $gettext("Unsaved changes"),
        icon: "fa fa-exclamation-triangle",
        acceptProps: {
            label: $gettext("Exit without saving"),
            severity: shouldUseContrast() ? CONTRAST : DANGER,
            style: { fontSize: "small" },
        },
        rejectProps: {
            label: $gettext("Go back"),
            severity: shouldUseContrast() ? CONTRAST : SECONDARY,
            style: { fontSize: "small" },
        },
        accept: () => {
            isEditing.value = false;
            finishSettingDisplayedRow(row);
        },
        reject: () =>
            lastFocusedElement.value &&
            commandeerFocusFromDataTable(lastFocusedElement.value),
    });
};

provide(displayedRowKey, { displayedRow, setDisplayedRow });
provide(isEditingKey, { isEditing, setIsEditing });
const selectedLanguage: Ref<Language> = ref(
    (arches.languages as Language[]).find(
        (lang) => lang.code === arches.activeLanguage,
    ) as Language,
);
provide(selectedLanguageKey, selectedLanguage);
const systemLanguage = ENGLISH; // TODO: get from settings
provide(systemLanguageKey, systemLanguage);

function memoizeLastActiveInput(event: FocusEvent) {
    if (!event.target) {
        return;
    }
    const element = event.target as HTMLElement;
    if (
        ["INPUT", "TEXTAREA"].includes(element.tagName) &&
        !element.classList.contains("p-tree-filter-input")
    ) {
        lastFocusedElement.value = element;
    }
}
</script>

<template>
    <div style="height: 100vh; padding-bottom: 2.5rem">
        <div class="list-editor-container">
            <ListHeader />
            <MainSplitter @focusout="memoizeLastActiveInput" />
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
        style="border-radius: 0rem"
        :draggable="false"
        :pt="{
            header: {
                style: {
                    background: 'var(--p-navigation-header-color)',
                    color: 'white',
                    borderRadius: '0rem',
                    marginBottom: '2rem',
                },
            },
            footer: {
                style: {
                    marginTop: '2rem',
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
