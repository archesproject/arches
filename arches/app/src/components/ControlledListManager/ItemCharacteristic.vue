<script setup lang="ts">
import arches from "arches";
import { computed, ref } from "vue";
import { useGettext } from "vue3-gettext";

import InputText from "primevue/inputtext";
import { useToast } from "primevue/usetoast";

import {
    postItemToServer,
    postListToServer,
} from "@/components/ControlledListManager/api.ts";
import type { Item } from "@/types/ControlledListManager.d";

const props: {
    item: Item;
    editable: boolean;
    field: "name" | "uri";
    label: string;
} = defineProps(["item", "editable", "field", "label"]);

const editing = ref(false);
const disabled = computed(() => {
    return !props.editable || !editing.value;
});

const dirtyFormValue = ref("");

const inputValue = computed({
    get() {
        return props.item[props.field];
    },
    set(newVal: string) {
        dirtyFormValue.value = newVal;
    },
});

const width = computed(() => {
    if (props.field === "uri") {
        return "100%";
    }
    return Math.max((props.item[props.field]).length + 2, 4) + "rem";
});

const toast = useToast();
const { $gettext } = useGettext();

const onSave = () => {
    editing.value = false;
    // eslint-disable-next-line vue/no-mutating-props
    props.item[props.field] = dirtyFormValue.value;

    const saveFn = Object.hasOwn(props.item, "items")
        ? postListToServer
        : postItemToServer;
    saveFn(props.item, toast, $gettext);
};
const onCancel = () => {
    editing.value = false;
    dirtyFormValue.value = props.item[props.field];
};
</script>

<template>
    <div class="characteristic">
        <h4>{{ props.label }}</h4>
        <InputText
            v-model="inputValue"
            type="text"
            class="control"
            :disabled="disabled"
            :style="{ width: width }"
        />
        <span
            v-if="props.editable && !editing"
            class="edit-controls"
        >
            <i
                role="button"
                tabindex="0"
                class="fa fa-pencil"
                :aria-label="arches.translations.edit"
                @click="editing = true"
                @keyup.enter="editing = true"
            />
        </span>
        <span
            v-if="props.editable && editing"
            class="edit-controls"
        >
            <i
                role="button"
                tabindex="0"
                class="fa fa-check"
                :aria-label="arches.translations.saveEdit"
                @click="onSave"
                @keyup.enter="onSave"
            />
            <i
                role="button"
                tabindex="0"
                class="fa fa-times"
                :aria-label="arches.translations.cancelEdit"
                @click="onCancel"
                @keyup.enter="onCancel"
            />
        </span>
    </div>
</template>

<style scoped>
h4,
input {
    font-size: 1.25rem;
}
.characteristic {
    margin: 1rem 1rem 2rem 1rem;
}
.characteristic input {
    text-align: center;
    border-width: 2px;
    height: 3rem;
}
.characteristic input[disabled] {
    background: var(--gray-400);
}
.edit-controls {
    margin-left: 1rem;
    display: inline-flex;
    justify-content: space-between;
    width: 4rem;
}
.edit-controls i {
    font-size: medium;
}
</style>
