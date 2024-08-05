<script setup lang="ts">
import { inject, provide } from "vue";

import ItemHeader from "@/arches_references/components/editor/ItemHeader.vue";
import ItemImages from "@/arches_references/components/editor/ItemImages.vue";
import ItemType from "@/arches_references/components/editor/ItemType.vue";
import ItemURI from "@/arches_references/components/editor/ItemURI.vue";
import ValueEditor from "@/arches_references/components/editor/ValueEditor.vue";

import {
    displayedRowKey,
    itemKey,
    ALT_LABEL,
    NOTE,
    PREF_LABEL,
} from "@/arches_references/constants.ts";

import type { Ref } from "vue";
import type { ControlledListItem } from "@/arches_references/types";

const { displayedRow: item } = inject(displayedRowKey) as unknown as {
    displayedRow: Ref<ControlledListItem>;
};
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
