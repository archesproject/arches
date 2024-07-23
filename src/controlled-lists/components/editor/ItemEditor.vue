<script setup lang="ts">
import { inject, provide } from "vue";

import ItemHeader from "@/controlled-lists/components/editor/ItemHeader.vue";
import ItemImages from "@/controlled-lists/components/editor/ItemImages.vue";
import ItemType from "@/controlled-lists/components/editor/ItemType.vue";
import ItemURI from "@/controlled-lists/components/editor/ItemURI.vue";
import ValueEditor from "@/controlled-lists/components/editor/ValueEditor.vue";

import {
    displayedRowKey,
    itemKey,
    ALT_LABEL,
    NOTE,
    PREF_LABEL,
} from "@/controlled-lists/constants.ts";

import type { DisplayedListItemRefAndSetter } from "@/controlled-lists/types";

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
