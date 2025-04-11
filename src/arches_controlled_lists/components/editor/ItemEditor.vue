<script setup lang="ts">
import { inject, provide } from "vue";

import ItemHeader from "@/arches_controlled_lists/components/editor/ItemHeader.vue";
import ItemImages from "@/arches_controlled_lists/components/editor/ItemImages.vue";
import ItemType from "@/arches_controlled_lists/components/editor/ItemType.vue";
import ItemURI from "@/arches_controlled_lists/components/editor/ItemURI.vue";
import ValueEditor from "@/arches_controlled_lists/components/editor/ValueEditor.vue";

import { ALT_LABEL, PREF_LABEL } from "@/arches_vue_utils/constants.ts";
import {
    displayedRowKey,
    itemKey,
    NOTE,
} from "@/arches_controlled_lists/constants.ts";

import type { Ref } from "vue";
import type { ControlledListItem } from "@/arches_controlled_lists/types";

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
