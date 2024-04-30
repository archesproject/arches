<script setup lang="ts">
import { computed, inject, ref } from "vue";
import { useGettext } from "vue3-gettext";

import InputText from "primevue/inputtext";
import { useToast } from "primevue/usetoast";

import { postItemToServer } from "@/components/ControlledListManager/api.ts";
import { itemKey } from "@/components/ControlledListManager/const.ts";

const props: { field: "uri", label: string } = defineProps(["field", "label"]);
const { item } = inject(itemKey);

const editing = ref(false);

const formValue = ref("");

const inputValue = computed({
    get() {
        return item.value[props.field];
    },
    set(newVal: string) {
        formValue.value = newVal;
    },
});

const toast = useToast();
const { $gettext } = useGettext();

const onSave = async () => {
    editing.value = false;
    const originalValue = item.value[props.field];
    item.value[props.field] = formValue.value;
    const success = await postItemToServer(item.value, toast, $gettext);
    if (!success) {
        item.value[props.field] = originalValue;
    }
};

const onCancel = () => {
    editing.value = false;
    formValue.value = item.value[props.field];
};
</script>

<template>
    <div class="characteristic">
        <InputText
            v-model="inputValue"
            type="text"
            :disabled="!editing"
            :aria-label="label"
            :placeholder="$gettext('Enter a URI')"
        />
        <span
            v-if="!editing"
            class="edit-controls"
        >
            <i
                role="button"
                tabindex="0"
                class="fa fa-pencil"
                :aria-label="$gettext('Edit')"
                @click="editing = true"
                @keyup.enter="editing = true"
            />
        </span>
        <span
            v-if="editing"
            class="edit-controls"
        >
            <i
                role="button"
                tabindex="0"
                class="fa fa-check"
                :aria-label="$gettext('Save edit')"
                @click="onSave"
                @keyup.enter="onSave"
            />
            <i
                role="button"
                tabindex="0"
                class="fa fa-times"
                :aria-label="$gettext('Cancel edit')"
                @click="onCancel"
                @keyup.enter="onCancel"
            />
        </span>
    </div>
</template>

<style scoped>
input {
    font-size: 1.25rem;
}

.characteristic {
    margin: 1rem 1rem 2rem 1rem;
    display: flex;
    align-items: center;
}

.characteristic input {
    text-align: center;
    height: 3rem;
    width: 100%;
}

.characteristic input[disabled] {
    text-align: left;
    opacity: 1;
    border: 0;
}

.edit-controls {
    margin-left: 1rem;
    display: inline-flex;
    justify-content: space-between;
    width: 4rem;
}

.edit-controls i {
    font-size: small;
    padding: 4px;
}
</style>
