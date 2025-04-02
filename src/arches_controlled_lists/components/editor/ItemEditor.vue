<script setup lang="ts">
import { inject, provide, useTemplateRef, watch } from "vue";

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

const prefLabelEditor = useTemplateRef("prefLabelEditor");
const altLabelEditor = useTemplateRef("altLabelEditor");
const noteEditor = useTemplateRef("noteEditor");
const uriEditor = useTemplateRef("uriEditor");
const imageEditor = useTemplateRef("imageEditor");

const { displayedRow: item } = inject(displayedRowKey) as unknown as {
    displayedRow: Ref<ControlledListItem>;
};
provide(itemKey, item);

const isEditing = inject("isEditing") as Ref<boolean>;

watch(
    [
        () => prefLabelEditor.value?.isEditing,
        () => altLabelEditor.value?.isEditing,
        () => noteEditor.value?.isEditing,
        () => uriEditor.value?.isEditing,
        () => imageEditor.value?.isEditing,
    ],
    () => {
        isEditing.value =
            prefLabelEditor.value?.isEditing ||
            altLabelEditor.value?.isEditing ||
            noteEditor.value?.isEditing ||
            uriEditor.value?.isEditing ||
            imageEditor.value?.isEditing ||
            false;
    },
);
</script>

<template>
    <template v-if="item">
        <ItemHeader />
        <ValueEditor
            ref="prefLabelEditor"
            :value-type="PREF_LABEL"
        />
        <ValueEditor
            ref="altLabelEditor"
            :value-type="ALT_LABEL"
        />
        <ItemType />
        <ValueEditor
            ref="noteEditor"
            :value-category="NOTE"
        />
        <ItemURI ref="uriEditor" />
        <ItemImages ref="imageEditor" />
    </template>
</template>
