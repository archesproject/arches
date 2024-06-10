<script setup lang="ts">
import arches from "arches";
import Cookies from "js-cookie";
import { inject } from "vue";
import { useGettext } from "vue3-gettext";

import FileUpload from "primevue/fileupload";
import { useToast } from "primevue/usetoast";

import ImageEditor from "@/components/ControlledListManager/ImageEditor.vue";

import { ARCHES_CHROME_BLUE } from "@/theme.ts";
import { itemKey, ERROR } from "@/components/ControlledListManager/constants.ts";

import type { Ref } from "vue";
import type { ControlledListItem } from "@/types/ControlledListManager";
import type {
    FileUploadBeforeSendEvent,
    FileUploadErrorEvent,
    FileUploadUploadEvent,
} from "primevue/fileupload";

const item = inject(itemKey) as Ref<ControlledListItem>;
const completed = 'Completed';

const { $gettext } = useGettext();
const toast = useToast();

const addHeader = (event: FileUploadBeforeSendEvent) => {
    const token = Cookies.get("csrftoken");
    if (token) {
        event.xhr.setRequestHeader("X-CSRFToken", token);
        event.formData.set("item_id", item.value!.id);
    }
};

const onUpload = (event: FileUploadUploadEvent) => {
    if (event.xhr.status !== 201) {
        onError(undefined);
    }
    const newImage = JSON.parse(event.xhr.responseText);
    item.value!.images.push(newImage);
};

const onError = (event?: FileUploadErrorEvent) => {
    toast.add({
        severity: ERROR,
        life: 8000,
        summary: event?.xhr?.statusText || $gettext("Image upload failed"),
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
            :show-upload-button="false"
            name="item_image"
            :pt="{
                buttonbar: { style: { border: '1px solid lightgray', borderRadius: '4px' } },
                file: ({ props }) => ({
                    style: {
                        display: (props as any).badgeValue === completed ? 'none' : ''
                    },
                }),
            }"
            @before-send="addHeader($event)"
            @upload="onUpload($event)"
            @error="onError($event)"
        />
        <div class="images">
            <ImageEditor
                v-for="image in item.images"
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

.images {
    margin-top: 1.5rem;
    gap: 1.5rem;
}

h4 {
    color: v-bind(ARCHES_CHROME_BLUE);
    margin-top: 0;
    font-size: 1.33rem;
}

p {
    font-size: 1.2rem;
}

.images {
    display: flex;
    flex-direction: column;
    gap: 32px;
}

:deep(input[type=file]) {
    /* override arches.css */
    /* PrimeVue uses a hidden input for screen readers */
    display: none;
}

:deep(.p-fileupload-content:empty) {
    display: none;
}
</style>
