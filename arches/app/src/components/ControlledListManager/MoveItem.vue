<script setup lang="ts">
import { ref } from "vue";

import Button from "primevue/button";
import Dialog from "primevue/dialog";
import Dropdown from "primevue/dropdown";

import type { Ref } from "@/types/Ref";

const visible: Ref<boolean> = defineModel({ required: true });
const newParent = ref();
const existingParent = "";
</script>

<template>
    <Dialog
        v-model:visible="visible"
        modal
        :draggable="false"
        :header="$gettext('Move Item')"
        :style="{ width: '40rem' }"
        :pt="{
            header: { style: { backgroundColor: '#2d3c4b' } },
            title: { style: { color: 'white', fontWeight: 600 } },
            content: { style: { display: 'flex', flexDirection: 'column', gap: '1rem' } },
            closeButtonIcon: { style: { color: 'white' } },
        }"
    >
        <div style="font-size: small;">
            {{ $gettext("Existing Parent: %{existingParent}", { existingParent }) }}
        </div>
        <div class="form-input">
            <span
                id="new-parent-label"
                style="margin-bottom: 5px"
            >{{ $gettext("New Parent") }}</span>
            <Dropdown
                v-model="language"
                aria-labelledby="new-parent-label"
                :options="[]"
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
                @click.stop="visible = false"
            />
            <Button
                type="button"
                class="save"
                :label="$gettext('Save')"
                :disabled="newParent !== existingParent"
                @click.stop="visible = false"
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
