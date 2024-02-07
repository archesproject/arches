<script setup lang="ts">
import arches from "arches";
import { computed, ref, watch } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import Dialog from "primevue/dialog";
import Dropdown from "primevue/dropdown";
import InputText from "primevue/inputtext";

import type {
    ControlledListItem,
    ValueType,
} from "@/types/ControlledListManager.d";

const props: {
    item: ControlledListItem;
    type: ValueType;
} = defineProps(["item", "type"]);

const visible = ref(false);
const value = ref("");
const language = ref(arches.activeLanguage);

const buttonLabel = computed(() => {
    return props.type === "prefLabel"
        ? $gettext("Add Preferred Label")
        : $gettext("Add Alternate Label");
});

watch(visible, () => {
    value.value = "";
});

const languages = ['en', 'nl']; // todo: wire up

const { $gettext } = useGettext();
const slateBlue = "#2d3c4b"; // todo: import from theme somewhere
</script>

<template>
    <button
        class="add-label"
        @click="visible = true"
    >
        <i
            class="fa fa-plus-circle"
            aria-hidden="true"
        />
        <span class="add-label-text">
            {{ buttonLabel }}
        </span>
    </button>
    <Dialog
        v-model:visible="visible"
        modal
        :draggable="false"
        :header="buttonLabel"
        :style="{ width: '40rem' }"
        :pt="{
            header: { style: { backgroundColor: '#2d3c4b' } },
            title: { style: { color: 'white' } },
            closeButtonIcon: { style: { color: 'white' } },
        }"
    >
        <div class="form-input">
            <label for="value">{{ $gettext("Item Label") }}</label>
            <InputText
                id="value"
                v-model="value"
                autocomplete="off"
            />
        </div>
        <div class="form-input">
            <span
                id="language-label"
                style="margin-bottom: 5px"
            >{{ $gettext("Language") }}</span>
            <Dropdown
                v-model="language"
                aria-labelledby="language-label"
                :options="languages"
                :pt="{
                    input: { style: { fontSize: 'small' } },
                    panel: { style: { fontSize: 'small' } },
                }"
            />
        </div>
        <div class="controls">
            <Button
                type="button"
                :label="arches.translations.save"
                :disabled="!value || !language"
                @click="visible = false"
            />
            <Button
                type="button"
                :label="arches.translations.cancelEdit"
                @click="visible = false"
            />
        </div>
    </Dialog>
</template>

<style scoped>
.add-label {
    display: flex;
    width: 100%;
    height: 4rem;
    color: v-bind(slateBlue);
}
.add-label > i,
.add-label > span {
    align-self: center;
}
.add-label-text {
    margin: 1rem;
    font-size: small;
    font-weight: 600;
}
.p-dialog-content {
    display: grid;
    gap: 2rem;
}
.form-input {
    display: flex;
    flex-direction: column;
    margin-bottom: 2rem;
    font-size: small;
}
label, .p.dropdown-label {
    font-size: small;
    color: #2d3c4b;
}
.controls {
    display: flex;
    gap: 1rem;
}
.controls > button {
    color: white;
    font-size: small;
    font-weight: 600;
}
.controls > button:nth-child(1) {
    background: #10b981;
    border-color: #10b981;
}
.controls > button:nth-child(2) {
    background: coral;
    border-color: coral;
}
</style>
