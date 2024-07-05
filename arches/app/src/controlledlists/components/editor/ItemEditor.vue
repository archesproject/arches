<script setup lang="ts">
import { inject, provide } from "vue";

import ItemHeader from "@/controlledlists/components/editor/ItemHeader.vue";
import ItemImages from "@/controlledlists/components/editor/ItemImages.vue";
import ItemType from "@/controlledlists/components/editor/ItemType.vue";
import ItemURI from "@/controlledlists/components/editor/ItemURI.vue";
import ValueEditor from "@/controlledlists/components/editor/ValueEditor.vue";

import {
    displayedRowKey,
    itemKey,
    ALT_LABEL,
    NOTE,
    PREF_LABEL,
} from "@/controlledlists/constants.ts";

import type { DisplayedListItemRefAndSetter } from "@/controlledlists/types";

const { displayedRow: item } = inject(
    displayedRowKey,
) as DisplayedListItemRefAndSetter;
provide(itemKey, item);
</script>

<template>
    <template v-if="item">
        <ItemHeader />
        <ValueEditor :value-type="PREF_LABEL" />
        <ValueEditor :value-type="ALT_LABEL" />
        <ItemType />
        <ValueEditor :value-category="NOTE" />
        <ItemURI />
        <ItemImages />
    </template>
</template>
