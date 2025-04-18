<script setup lang="ts">
import { inject } from "vue";
import { useGettext } from "vue3-gettext";

import { getItemLabel } from "@/arches_vue_utils/utils.ts";
import {
    itemKey,
    selectedLanguageKey,
    systemLanguageKey,
} from "@/arches_controlled_lists/constants.ts";

import type { Ref } from "vue";
import type { Language } from "@/arches_vue_utils/types";
import type { ControlledListItem } from "@/arches_controlled_lists/types";

const selectedLanguage = inject(selectedLanguageKey) as Ref<Language>;
const systemLanguage = inject(systemLanguageKey) as Language;
const item = inject(itemKey) as Ref<ControlledListItem>;

const { $gettext } = useGettext();

const iconLabel = (item: ControlledListItem) => {
    return item.guide ? $gettext("Guide Item") : $gettext("Indexable Item");
};
</script>

<template>
    <div class="item-header-container">
        <div class="item-header">
            <i
                class="pi pi-tag item-header-icon"
                :aria-label="$gettext('Item')"
            ></i>
            <h3 class="item-label">
                {{
                    getItemLabel(item, selectedLanguage.code, systemLanguage.code)
                        .value
                }}
            </h3>
            <span class="item-type">{{ iconLabel(item) }}</span>
        </div>
        <div class="item-url">
            <a
                v-if="item.uri"
                :href="item.uri"
                rel="noreferrer"
                target="_blank"
            >
                {{ item.uri }}
            </a>
        </div>
    </div>
</template>

<style scoped>
.item-header-container {
    display: flex;
    flex-direction: column;
    gap: 0rem;
    margin: 1rem 1rem 0rem 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--p-content-border-color);
    width: 100%;
}

.item-header {
    display: flex;
}

.item-header-icon {
    padding: .5rem .5rem;
    align-items: baseline;
}

.item-label {
    padding: 0 .5rem 0 0;
    font-weight: 400;
    margin: 0;
    font-size: 1.8rem;
}

.item-url {
    padding: 0 2.25rem;
}

.item-type {
    font-size: small;
    font-weight: 200;
    padding: .25rem 0 0 0;
}

a {
    font-size: small;
    color: var(--p-text-muted-color);
    text-decoration: underline;
}
</style>
