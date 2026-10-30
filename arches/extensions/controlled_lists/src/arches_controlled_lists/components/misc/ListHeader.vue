<script setup lang="ts">
import { computed, inject } from "vue";
import { useGettext } from "vue3-gettext";

import {
    displayedRowKey,
    selectedLanguageKey,
    systemLanguageKey,
} from "@/arches_controlled_lists/constants.ts";
import { dataIsList, getItemLabel } from "@/arches_controlled_lists/utils.ts";

import type { Ref } from "vue";
import type {
    ControlledList,
    ControlledListItem,
    Language,
    Selectable,
} from "@/arches_controlled_lists/types";

const { $gettext } = useGettext();

const { displayedRow } = inject<{ displayedRow: Ref<Selectable> }>(
    displayedRowKey,
)!;
const selectedLanguage = inject(selectedLanguageKey) as Ref<Language>;
const systemLanguage = inject(systemLanguageKey) as Language;

const heading = computed(() => {
    if (!displayedRow.value) {
        return $gettext("List Editor");
    }
    if (dataIsList(displayedRow.value)) {
        return $gettext(
            "List Editor > %{listName}",
            { listName: (displayedRow.value as ControlledList).name },
            true, // turn off escaping: vue template sanitizes
        );
    }
    return $gettext(
        "Item Editor > %{itemLabel}",
        {
            itemLabel: getItemLabel(
                displayedRow.value as ControlledListItem,
                selectedLanguage.value.code,
                systemLanguage.code,
            ).value,
        },
        true, // turn off escaping: vue template sanitizes
    );
});
</script>

<template>
    <div class="header">
        <i
            class="fa fa-inverse fa-list"
            aria-hidden="true"
        />
        <h2 style="margin: 1rem">{{ heading }}</h2>
    </div>
</template>

<style scoped>
.header {
    display: flex;
    align-items: center;
    background: var(--p-navigation-header-color);
    color: var(--p-slate-50);
    height: 5.25rem;
}

i {
    margin-inline-start: 1rem;
    margin-top: 0.25rem;
}
</style>
