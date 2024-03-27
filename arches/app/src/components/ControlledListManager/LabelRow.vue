<script setup lang="ts">
import { computed, ref } from "vue";
import { useGettext } from "vue3-gettext";

import EditLabel from "@/components/ControlledListManager/EditLabel.vue";
import { ALT_LABEL, PREF_LABEL } from "@/components/ControlledListManager/const.ts";

import type { Label } from "@/types/ControlledListManager";

const props: {
    label: Label,
    onDelete: (labelId: Label) => Promise<void>,
} = defineProps(["label", "onDelete"]);

const modalVisible = ref(false);

const { $gettext } = useGettext();
const header = computed(() => {
    switch (props.label.valuetype) {
        case PREF_LABEL:
            return $gettext("Edit Preferred Label");
        case ALT_LABEL:
            return $gettext("Edit Alternate Label");
        default:
            throw new Error();
    }
});
</script>

<template>
    <div class="label-container">
        <span class="item-label">{{ props.label.value }}</span>
        <div class="label-end">
            <span class="controls">
                <button @click="props.onDelete(props.label)">
                    {{ $gettext("Delete") }}
                </button>
                <button @click="modalVisible = true">
                    {{ $gettext("Edit") }}
                </button>
            </span>
            <span class="item-label language">{{ props.label.language }}</span>
        </div>
    </div>
    <EditLabel
        v-model="modalVisible"
        :header
        :label
        :is-insert="false"
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
.item-label {
    color: black;
    align-self: center;
    font-size: small;
}
.label-end {
    display: inline-flex;
}
.controls {
    display: inline-flex;
    justify-content: space-between;
    min-width: 7rem;
}
button {
    color: var(--blue-500);
    font-size: small;
    background: none;
    border: none;
    /* when adjusting padding, ensure action area of button is not inaccessibly slim */
    /* I'm showing ~37px, which is already below the MDN recommendation of 44 */
    padding: 1rem;
}
.item-label.language {
    border-radius: 1px;
    background: var(--gray-200);
    padding: 0.5rem;
}
</style>
