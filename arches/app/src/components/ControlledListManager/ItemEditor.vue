<script setup lang="ts">
import { inject, provide } from "vue";

import ItemHeader from "@/components/ControlledListManager/ItemHeader.vue";
import ItemImages from "@/components/ControlledListManager/ItemImages.vue";
import ItemType from "@/components/ControlledListManager/ItemType.vue";
import ItemURI from "@/components/ControlledListManager/ItemURI.vue";
import ValueEditor from "@/components/ControlledListManager/ValueEditor.vue";

import {
    displayedRowKey,
    itemKey,
    ALT_LABEL,
    NOTE,
    PREF_LABEL,
} from "@/components/ControlledListManager/constants.ts";

import type { DisplayedListItemRefAndSetter } from "@/types/ControlledListManager";

const { displayedRow: item } = inject(displayedRowKey) as DisplayedListItemRefAndSetter;
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
