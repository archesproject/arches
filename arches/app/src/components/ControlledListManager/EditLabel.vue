<script setup lang="ts">
import arches from "arches";
import { computed, ref } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import Dialog from "primevue/dialog";
import Dropdown from "primevue/dropdown";
import InputText from "primevue/inputtext";
import { useToast } from "primevue/usetoast";

import { createLabel } from "@/components/ControlledListManager/api.ts";

import type {
    ControlledListItem,
    Label,
    LanguageMap,
    ValueType,
} from "@/types/ControlledListManager.d";

const props: {
    item: ControlledListItem;
    header: string;
    languageMap: LanguageMap;
    type: ValueType;
    insertLabel: (label: Label) => Promise<Label>;
} = defineProps(["item", "header", "languageMap", "type", "insertLabel"]);

const value = ref("");
const language = ref(arches.activeLanguage);

const visible = defineModel<boolean>({ required: true });

const languageOptions = computed(() => {
    if (!props.languageMap) {
        return [];
    }
    return (
        Object.entries(props.languageMap).map(([code, label]) => {
            return {
                label,
                code,
            };
        })
    );
});

const toast = useToast();
const { $gettext } = useGettext();
const staticItemLabel = $gettext("Item Label");
const staticLanguageLabel = $gettext("Language");

const onSave = async () => {
    const newLabel = await createLabel(
        {
            value: value.value,
            language: language.value,
            valuetype: props.type,
            itemId: props.item.id,
        },
        toast,
        $gettext,
    );

    if (newLabel) {
        visible.value = false;
        value.value = "";

        props.insertLabel(newLabel);
    }
};
</script>

<template>
    <Dialog
        v-model:visible="visible"
        modal
        :draggable="false"
        :header
        :style="{ width: '40rem' }"
        :pt="{
            header: { style: { backgroundColor: '#2d3c4b' } },
            title: { style: { color: 'white' } },
            closeButtonIcon: { style: { color: 'white' } },
        }"
    >
        <div class="form-input">
            <label for="value">{{ staticItemLabel }}</label>
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
            >{{ staticLanguageLabel }}</span>
            <Dropdown
                v-model="language"
                aria-labelledby="language-label"
                :options="languageOptions"
                option-label="label"
                option-value="code"
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
                @click="onSave"
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
