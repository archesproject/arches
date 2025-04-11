<script setup lang="ts">
import arches from "arches";
import Cookies from "js-cookie";
import { inject, useTemplateRef } from "vue";
import { useGettext } from "vue3-gettext";

import FileUpload from "primevue/fileupload";
import { useToast } from "primevue/usetoast";

import {
    itemKey,
    CONTRAST,
    DEFAULT_ERROR_TOAST_LIFE,
    ERROR,
    PRIMARY,
} from "@/arches_controlled_lists/constants.ts";
import { shouldUseContrast } from "@/arches_controlled_lists/utils.ts";
import ImageEditor from "@/arches_controlled_lists/components/editor/ImageEditor.vue";

import type { Ref } from "vue";
import type { ControlledListItem } from "@/arches_controlled_lists/types";
import type {
    FileUploadBeforeSendEvent,
    FileUploadErrorEvent,
    FileUploadProps,
    FileUploadState,
    FileUploadUploadEvent,
} from "primevue/fileupload";

interface FileUploadInternals {
    props: FileUploadProps;
    state: FileUploadState;
}

const { $gettext } = useGettext();
const toast = useToast();

const item = inject(itemKey) as Ref<ControlledListItem>;
const editors = useTemplateRef("editors");

const addHeader = (event: FileUploadBeforeSendEvent) => {
    const token = Cookies.get("csrftoken");
    if (token) {
        event.xhr.setRequestHeader("X-CSRFToken", token);
        event.formData.set("list_item_id", item.value.id);
    }
};

const upload = (event: FileUploadUploadEvent) => {
    if (event.xhr.status !== 201) {
        showError(event);
        return;
    }
    const newImage = JSON.parse(event.xhr.responseText);
    item.value.images.push(newImage);
};

const showError = (event?: FileUploadErrorEvent | FileUploadUploadEvent) => {
    toast.add({
        severity: ERROR,
        life: DEFAULT_ERROR_TOAST_LIFE,
        summary: event?.xhr?.statusText || $gettext("Image upload failed"),
        detail: JSON.parse(event?.xhr?.responseText ?? "{}").message,
    });
};
</script>

<template>
    <div class="images-container">
        <h4>{{ $gettext("Images") }}</h4>
        <FileUpload
            accept="image/*"
            :url="arches.urls.controlled_list_item_image_add"
            :auto="true"
            :max-file-size="5e6"
            :file-limit="10"
            :preview-width="250"
            :with-credentials="true"
            :show-cancel-button="false"
            :show-upload-button="false"
            :choose-button-props="{
                severity: shouldUseContrast() ? CONTRAST : PRIMARY,
            }"
            choose-icon="fa fa-plus-circle"
            :choose-label="$gettext('Upload an image')"
            name="item_image"
            :pt="{
                content: ({ props, state }: FileUploadInternals) => {
                    const done = [0, 100].includes(state.progress);
                    return {
                        style: { display: done ? 'none' : '' },
                    };
                },
                pcChooseButton: { root: { style: { fontSize: 'smaller' } } },
            }"
            @before-send="addHeader($event)"
            @upload="upload($event)"
            @error="showError($event)"
        />
        <div class="images">
            <ImageEditor
                v-for="image in item.images"
                ref="editors"
                :key="image.id"
                :image="image"
            />
            <p v-if="!item.images.length">
                {{ $gettext("No images.") }}
            </p>
        </div>
    </div>
</template>

<style scoped>
.images-container {
    margin: 1rem 1rem 3rem 1rem;
    display: flex;
    flex-direction: column;
    width: 100%;
}

h4 {
    margin-top: 0;
}

p {
    font-size: 1.2rem;
}

.images {
    margin-top: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 3rem;
}

:deep(input[type="file"]) {
    /* override arches.css */
    /* PrimeVue uses a hidden input for screen readers */
    display: none;
}

:deep(.p-fileupload-content:empty) {
    display: none;
}
</style>
