<script setup lang="ts">
import { inject, provide } from "vue";

import ItemHeader from "@/arches-references/components/editor/ItemHeader.vue";
import ItemImages from "@/arches-references/components/editor/ItemImages.vue";
import ItemType from "@/arches-references/components/editor/ItemType.vue";
import ItemURI from "@/arches-references/components/editor/ItemURI.vue";
import ValueEditor from "@/arches-references/components/editor/ValueEditor.vue";

import {
    displayedRowKey,
    itemKey,
    ALT_LABEL,
    NOTE,
    PREF_LABEL,
} from "@/arches-references/constants.ts";

import type { DisplayedListItemRefAndSetter } from "@/arches-references/types";

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
