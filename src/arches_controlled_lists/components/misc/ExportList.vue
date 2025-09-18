<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useGettext } from "vue3-gettext";

import { useToast } from "primevue/usetoast";
import Button from "primevue/button";
import Dialog from "primevue/dialog";
import MultiSelect from "primevue/multiselect";

import { exportList } from "@/arches_controlled_lists/api.ts";
import {
    DEFAULT_ERROR_TOAST_LIFE,
    ERROR,
} from "@/arches_controlled_lists/constants.ts";

import type { TreeNode } from "primevue/treenode";

const { $gettext } = useGettext();
const toast = useToast();

const props = defineProps<{
    lists: TreeNode[];
}>();

const emit = defineEmits<{
    (e: "exported"): void;
}>();

const visible = ref(true);
const listOptions = ref();
const selectedListIds = ref<string[]>([]);

function extractLists() {
    return (listOptions.value = props.lists.map((node) => ({
        id: node.data.id,
        name: node.data.name,
    })));
}

async function exportToSKOS() {
    const file = await exportList(selectedListIds.value).catch(
        (error: Error) => {
            toast.add({
                severity: ERROR,
                life: DEFAULT_ERROR_TOAST_LIFE,
                summary: $gettext("Unable to export"),
                detail: error.message,
            });
        },
    );
    if (file) {
        const url = window.URL.createObjectURL(
            new Blob([file], { type: "application/xml" }),
        );
        const download = document.createElement("a");
        download.href = url;
        download.setAttribute("download", `${"PLACEHOLDER"}.xml`);
        document.body.appendChild(download);
        download.click();
        document.body.removeChild(download);
        emit("exported");
    }
}

onMounted(() => {
    extractLists();
});
</script>

<template>
    <Dialog
        v-model:visible="visible"
        position="center"
        :draggable="false"
        :header="$gettext('Export Controlled Lists')"
        :close-on-escape="true"
        :modal="true"
        :pt="{
            root: {
                style: {
                    minWidth: '50rem',
                    borderRadius: '0',
                },
            },
            header: {
                style: {
                    background: 'var(--p-navigation-header-color)',
                    color: 'var(--p-dialog-header-text-color)',
                    borderRadius: '0',
                },
            },
        }"
    >
        <template #default>
            <MultiSelect
                v-model="selectedListIds"
                :options="listOptions"
                option-label="name"
                option-value="id"
                :placeholder="$gettext('Select lists to export')"
                :filter="true"
                :filter-placeholder="$gettext('Search lists...')"
                :style="{ width: '100%' }"
                :max-selected-labels="3"
                display="chip"
                :show-clear="true"
            />
        </template>
        <template #footer>
            <Button
                :label="$gettext('Cancel')"
                type="button"
                @click="visible = false"
            />
            <Button
                :label="$gettext('Export')"
                type="submit"
                :disabled="!selectedListIds.length"
                @click="exportToSKOS()"
            />
        </template>
    </Dialog>
</template>

<style scoped>
.export-button {
    font-size: 1.25rem;
    border-radius: 0;
}
</style>
