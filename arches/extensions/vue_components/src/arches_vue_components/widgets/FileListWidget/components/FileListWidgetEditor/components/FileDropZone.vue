<script setup lang="ts">
import { computed, useId } from "vue";
import { useGettext } from "vue3-gettext";

import type { CardXNodeXWidgetData } from "@/arches_vue_components/types";

const { $gettext } = useGettext();

const {
    openFileChooser,
    cardXNodeXWidgetData = undefined,
    isDisabled,
    acceptedFileTypes,
} = defineProps<{
    openFileChooser: () => void;
    cardXNodeXWidgetData?: CardXNodeXWidgetData;
    isDisabled: boolean;
    acceptedFileTypes: string[];
}>();

const disabledReasonId = useId();

// pointer-events: none only blocks the mouse; keyboard activation still fires.
function onActivate() {
    if (!isDisabled) {
        openFileChooser();
    }
}

const displayFileTypes = computed(() => {
    if (!acceptedFileTypes.length) {
        return undefined;
    }
    const mimeWildcardLabels: Record<string, string> = {
        "image/*": $gettext("Images"),
    };
    return acceptedFileTypes
        .map((fileType) => mimeWildcardLabels[fileType] ?? fileType)
        .join(", ");
});
</script>

<template>
    <div
        v-tooltip="{
            value: isDisabled
                ? $gettext('Maximum number of files reached.')
                : null,
            pt: {
                arrow: {
                    style: { display: 'none' },
                },
                text: {
                    style: {
                        fontSize: '1rem',
                        paddingBottom: '0.75rem',
                        paddingInlineStart: '0.25rem',
                    },
                },
            },
        }"
    >
        <button
            :id="cardXNodeXWidgetData?.node.alias"
            type="button"
            class="upload-container"
            :class="{ 'p-disabled': isDisabled }"
            :aria-disabled="isDisabled ? 'true' : undefined"
            :aria-describedby="isDisabled ? disabledReasonId : undefined"
            @click="onActivate"
        >
            <i
                class="pi pi-cloud-upload upload-icon"
                aria-hidden="true"
            />
            <span class="upload-title">
                {{ $gettext("Upload Files") }}
            </span>
            <span class="upload-subtitle">
                {{ $gettext("Drag & drop files here or click to browse") }}
            </span>
            <span
                v-if="displayFileTypes"
                class="accepted-types"
            >
                {{
                    $gettext("Accepted file types: %{acceptedFileTypeLabels}", {
                        acceptedFileTypeLabels: displayFileTypes,
                    })
                }}
            </span>
        </button>
        <span
            v-if="isDisabled"
            :id="disabledReasonId"
            class="p-hidden-accessible"
        >
            {{ $gettext("Maximum number of files reached.") }}
        </span>
    </div>
</template>

<style scoped>
.upload-container {
    display: flex;
    flex-direction: column;
    width: 100%;
    font: inherit;
    color: inherit;
    text-align: center;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    border: 0.125rem dashed var(--p-content-border-color);
    border-radius: 0.5rem;
    background-color: var(--p-surface-50);
    cursor: pointer;
}

.upload-icon {
    font-size: 2rem;
    color: var(--p-primary-color);
    margin-bottom: 0.5rem;
}

.upload-title {
    font-weight: bold;
    color: var(--p-text-color);
    margin-bottom: 0.25rem;
}

.upload-subtitle {
    font-size: 1rem;
    color: var(--p-text-muted-color);
}

.accepted-types {
    font-size: 0.875rem;
    color: var(--p-text-muted-color);
    margin-top: 0.25rem;
}

.upload-container {
    outline: none;
}
.upload-container:focus {
    outline: 0.25rem solid var(--p-primary-color);
    outline-offset: 0.25rem;
    border-radius: var(--p-content-border-radius, 1rem);
}
</style>
