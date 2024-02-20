<script setup lang="ts">
import arches from "arches";
import { computed, ref } from "vue";
import { useGettext } from "vue3-gettext";

import EditLabel from "@/components/ControlledListManager/EditLabel.vue";

import type { ControlledListItem, Label, LanguageMap } from "@/types/ControlledListManager";

const props: {
    item: ControlledListItem,
    label: Label,
    languageMap: LanguageMap,
    onDelete: (labelId: Label) => Promise<void>,
} = defineProps(["item", "label", "languageMap", "onDelete"]);

const visible = ref(false);

const { $gettext } = useGettext();
const header = computed(() => {
    return props.label.valuetype === "prefLabel"
        ? $gettext("Edit Preferred Label")
        : $gettext("Edit Alternate Label");
});

</script>

<template>
    <div class="label-container">
        <span class="label">{{ props.label.value }}</span>
        <div class="label-end">
            <span class="controls">
                <button @click="props.onDelete(props.label)">
                    {{ arches.translations.delete }}
                </button>
                <button @click="visible = true">
                    {{ arches.translations.edit }}
                </button>
            </span>
            <span class="label language">{{ props.label.language }}</span>
        </div>
    </div>
    <EditLabel
        v-model="visible"
        :item
        :header
        :language-map
        :label
        :on-insert="null"
    />
</template>

<style scoped>
.label-container {
    display: flex;
    justify-content: space-between;
    background: #f3fbfd;
    border: 1px solid lightgray;
}
span {
    margin: 1rem;
}
.label {
    color: black;
    align-self: center;
}
.controls {
    display: inline-flex;
    justify-content: space-between;
    min-width: 7rem;
}
button {
    color: var(--blue-500);
    font-size: smaller;
    background: none;
    border: none;
    /* when adjusting padding, ensure action area of button is not inaccessibly slim */
    /* I'm showing ~37px, which is already below the MDN recommendation of 44 */
    padding: 1rem;
}
.label.language {
    width: 4rem;
    height: 2rem;
    border-radius: 1px;
    background: var(--gray-200);
}
</style>
