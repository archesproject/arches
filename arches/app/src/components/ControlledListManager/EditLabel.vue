<script setup lang="ts">
import arches from "arches";
import { inject, ref } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import Dialog from "primevue/dialog";
import Dropdown from "primevue/dropdown";
import InputText from "primevue/inputtext";
import { useToast } from "primevue/usetoast";

import { upsertLabel } from "@/components/ControlledListManager/api.ts";
import { itemKey } from "@/components/ControlledListManager/const.ts";

import type { Ref } from "@/types/Ref";
import type {
    Label,
    NewLabel,
} from "@/types/ControlledListManager";

const props: {
    header: string;
    label: Label | NewLabel;
    isInsert: boolean;
} = defineProps(["header", "label", "isInsert"]);
const { appendItemLabel, updateItemLabel } = inject(itemKey);

const value = ref(props.label.value);
const language = ref(props.label.language);

const visible: Ref<boolean> = defineModel({ required: true });

const toast = useToast();
const { $gettext } = useGettext();

const onSave = async () => {
    const upsertedLabel: Label = await upsertLabel(
        {
            id: props.label.id,
            value: value.value,
            language: language.value,
            valuetype: props.label.valuetype,
            item_id: props.label.item_id,
        },
        toast,
        $gettext,
    );

    if (upsertedLabel) {
        if (props.isInsert) {
            appendItemLabel.value(upsertedLabel);
            value.value = "";
        } else {
            updateItemLabel.value(upsertedLabel);
        }
        visible.value = false;
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
            title: { style: { color: 'white', fontWeight: 600 } },
            content: { style: { paddingTop: '1rem' } },
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
                :options="arches.languages"
                option-label="name"
                option-value="code"
                :pt="{
                    input: { style: { fontFamily: 'inherit', fontSize: 'small' } },
                    panel: { style: { fontSize: 'small' } },
                }"
            />
        </div>
        <div class="controls">
            <Button
                type="button"
                class="delete"
                :label="$gettext('Cancel edit')"
                @click="visible = false; value = props.label.value"
            />
            <Button
                type="button"
                class="save"
                :label="$gettext('Save')"
                :disabled="!value || !language"
                @click="onSave"
            />
        </div>
    </Dialog>
</template>

<style scoped>
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
    justify-content: end;
}
.controls > button {
    color: white;
    font-size: small;
    font-weight: 600;
}
button.save {
    background: #10b981;
    border-color: #10b981;
}
button.delete {
    background: coral;
    border-color: coral;
}
</style>
