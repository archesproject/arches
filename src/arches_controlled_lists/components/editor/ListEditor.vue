<script setup lang="ts">
import { inject } from "vue";
import { useGettext } from "vue3-gettext";

import { useToast } from "primevue/usetoast";
import Button from "primevue/button";

import { displayedRowKey } from "@/arches_controlled_lists/constants.ts";
import ListCharacteristic from "@/arches_controlled_lists/components/editor/ListCharacteristic.vue";
import ListSearchable from "@/arches_controlled_lists/components/editor/ListSearchable.vue";
import ReferenceNodeLink from "@/arches_controlled_lists/components/editor/ReferenceNodeLink.vue";

import { exportList } from "@/arches_controlled_lists/api.ts";
import {
    DEFAULT_ERROR_TOAST_LIFE,
    ERROR,
} from "@/arches_controlled_lists/constants.ts";

import type { Ref } from "vue";
import type { ControlledList } from "@/arches_controlled_lists/types";

const { $gettext } = useGettext();
const toast = useToast();

const { displayedRow: list } = inject<{ displayedRow: Ref<ControlledList> }>(
    displayedRowKey,
)!;

async function exportToSKOS() {
    const file = await exportList([list.value.id]).catch((error: Error) => {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("Unable to import SKOS file"),
            detail: error.message,
        });
    });
    if (file) {
        const url = window.URL.createObjectURL(
            new Blob([file], { type: "application/xml" }),
        );
        const download = document.createElement("a");
        download.href = url;
        download.setAttribute("download", `${list.value.name}.xml`);
        document.body.appendChild(download);
        download.click();
        document.body.removeChild(download);
    }
}
</script>

<template>
    <template v-if="list">
        <div class="controlled-list-header">
            <h3 class="list-label">
                <i
                    class="pi pi-folder list-header-icon"
                    :aria-label="$gettext('List')"
                ></i>
                <span>{{ list.name }}</span>
            </h3>
            <Button
                :label="$gettext('Export')"
                icon="pi pi-external-link"
                :aria-label="
                    $gettext('Export list %{list}', { list: list.name })
                "
                class="export-button"
                @click="exportToSKOS()"
            ></Button>
        </div>
        <div>
            <ListCharacteristic
                :editable="true"
                :label="$gettext('Name')"
            />
            <ListCharacteristic
                class="charactistic-label"
                :editable="false"
                :label="$gettext('Dynamic')"
                :style="{ width: '4rem' }"
            />
            <ListSearchable />
            <div class="nodes-container">
                <h4 class="nodes-container-title">
                    {{ $gettext("List used by these nodes") }}
                </h4>
                <div class="nodes">
                    <div
                        v-for="node in list.nodes"
                        :key="node.id"
                    >
                        <ReferenceNodeLink :node />
                    </div>
                    <div
                        v-if="list.nodes.length === 0"
                        :style="{ fontSize: 'small' }"
                    >
                        {{ $gettext("None") }}
                    </div>
                </div>
            </div>
        </div>
    </template>
</template>

<style scoped>
.controlled-list-header {
    display: flex;
    flex-direction: row;
    gap: 0rem;
    margin: 1rem 1rem 0rem 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--p-content-border-color);
    justify-content: space-between;
}

.list-label {
    padding: 0 0.5rem 0 0;
    font-weight: 400;
    margin: 0;
    font-size: 1.75rem;
}

.list-header-icon {
    padding: 0.5rem 0.5rem;
}

.export-button {
    font-size: 1.25rem;
    border-radius: 0;
}

.nodes-container {
    margin: 1rem 1rem 2rem 1rem;
}

.nodes-container-title {
    padding: 0 0.5rem 0 0;
    font-weight: 400;
    margin: 0.5rem 0 0.5rem 0;
    font-size: 1.75rem;
}

.nodes {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
}
</style>
