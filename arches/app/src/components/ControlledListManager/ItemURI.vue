<script setup lang="ts">
import { computed, inject, ref } from "vue";
import { useGettext } from "vue3-gettext";

import InputText from "primevue/inputtext";
import { useToast } from "primevue/usetoast";

import { ARCHES_CHROME_BLUE } from "@/theme.ts";
import { postItemToServer } from "@/components/ControlledListManager/api.ts";
import { itemKey } from "@/components/ControlledListManager/constants.ts";

import type { Ref } from "vue";
import type { ControlledListItem } from "@/types/ControlledListManager";

const item = inject(itemKey) as Ref<ControlledListItem>;

const editing = ref(false);

const formValue = ref("");

const inputValue = computed({
    get() {
        return item.value.uri;
    },
    set(newVal: string) {
        formValue.value = newVal;
    },
});

const toast = useToast();
const { $gettext } = useGettext();

const uriHeading = $gettext("List Item URI");
const uriSubheading = $gettext("Optionally, provide a URI for your list item. Useful if your list item is formally defined in a thesaurus or authority document.");

const onSave = async () => {
    editing.value = false;
    const originalValue = item.value.uri;
    item.value.uri = formValue.value;
    const success = await postItemToServer(item.value, toast, $gettext);
    if (!success) {
        item.value.uri = originalValue;
    }
};

const onCancel = () => {
    editing.value = false;
    formValue.value = item.value.uri;
};
</script>

<template>
    <div class="uri-container">
        <h4>{{ uriHeading }}</h4>
        <p>{{ uriSubheading }}</p>
        <div class="characteristic">
            <InputText
                v-model="inputValue"
                type="text"
                :disabled="!editing"
                :aria-label="$gettext('URI')"
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
    </div>
</template>

<style scoped>
.uri-container {
    margin: 1rem 1rem 3rem 1rem;
    display: flex;
    flex-direction: column;
    width: 100%;
}
h4 {
    color: v-bind(ARCHES_CHROME_BLUE);
    margin-top: 0;
    font-size: small;
}

p {
    font-weight: normal;
    margin-top: 0;
    font-size: small;
}

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
