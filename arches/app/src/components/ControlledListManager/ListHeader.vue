<script setup lang="ts">
import { computed, inject } from "vue";
import { useGettext } from "vue3-gettext";

import { ARCHES_CHROME_BLUE } from "@/theme.ts";
import { displayedRowKey, selectedLanguageKey } from "@/components/ControlledListManager/constants.ts";
import { bestLabel } from "@/components/ControlledListManager/utils.ts";

import type { Ref } from "vue";
import type { Language } from "@/types/arches";
import type {
    ControlledList,
    ControlledListItem,
    DisplayedRowRefAndSetter,
} from "@/types/ControlledListManager";

const { $gettext } = useGettext();

const { displayedRow } = inject(displayedRowKey) as DisplayedRowRefAndSetter;
const selectedLanguage = inject(selectedLanguageKey) as Ref<Language>;

const heading = computed(() => {
    if (!displayedRow.value) {
        return $gettext("List Editor");
    }
    if ((displayedRow.value as ControlledListItem).depth === undefined) {
        return $gettext(
            "List Editor > %{listName}",
            { listName: (displayedRow.value as ControlledList).name },
            true, // disable HTML escaping: RDM Admins are trusted users
        );
    }
    return $gettext(
        "Item Editor > %{bestLabel}",
        { bestLabel: bestLabel(displayedRow.value, selectedLanguage.value.code).value },
        true, // disable HTML escaping: RDM Admins are trusted users
    );
});
</script>

<template>
    <div
        class="header"
        :style="{ background: ARCHES_CHROME_BLUE }"
    >
        <i
            class="fa fa-inverse fa-list"
            aria-hidden="true"
        />
        <h2>{{ heading }}</h2>
    </div>
</template>

<style scoped>
.header {
    display: flex;
    align-items: center;
}
i {
    margin-left: 1rem;
    margin-top: 0.25rem;
}
h2 {
    font-size: 1.5rem;
    margin: 1rem;
    color: white;
}
</style>
