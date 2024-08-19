<script setup lang="ts">
import { computed, inject } from "vue";
import { useGettext } from "vue3-gettext";

import {
    displayedRowKey,
    selectedLanguageKey,
} from "@/arches_references/constants.ts";
import { bestLabel, dataIsList } from "@/arches_references/utils.ts";

import type { Ref } from "vue";
import type { Language } from "@/arches/types";
import type {
    ControlledList,
    ControlledListItem,
    Selectable,
} from "@/arches_references/types";

const { $gettext } = useGettext();

const { displayedRow } = inject(displayedRowKey) as unknown as {
    displayedRow: Ref<Selectable>;
};
const selectedLanguage = inject(selectedLanguageKey) as Ref<Language>;

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
        "Item Editor > %{bestLabel}",
        {
            bestLabel: bestLabel(
                displayedRow.value as ControlledListItem,
                selectedLanguage.value.code,
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
    background: var(--p-navigation);
    color: white;
}

i {
    margin-left: 1rem;
    margin-top: 0.25rem;
}
</style>
