<script setup lang="ts">
import arches from "arches";
import Cookies from "js-cookie";
import { inject } from "vue";
import { useGettext } from "vue3-gettext";

import FileUpload from "primevue/fileupload";

import ImageEditor from "@/components/ControlledListManager/ImageEditor.vue";

import { ARCHES_CHROME_BLUE } from "@/theme.ts";
import { itemKey } from "@/components/ControlledListManager/constants.ts";

import type { Ref } from "vue";
import type { ControlledListItem } from "@/types/ControlledListManager";
import type { FileUploadBeforeSendEvent, FileUploadUploadEvent } from "primevue/fileupload";

const item = inject(itemKey) as Ref<ControlledListItem>;

const { $gettext } = useGettext();

const addHeader = (event: FileUploadBeforeSendEvent) => {
    const token = Cookies.get("csrftoken");
    if (token) {
        event.xhr.setRequestHeader("X-CSRFToken", token);
        event.formData.set("item_id", item.value!.id);
    }
};

const onUpload = (event: FileUploadUploadEvent) => {
    if (event.xhr.status !== 201) {
        return;
    }
    const newImage = JSON.parse(event.xhr.responseText);
    item.value!.images.push(newImage);
};
</script>

<template>
    <h4>{{ $gettext("Images") }}</h4>
    <FileUpload
        accept="image/*"
        :url="arches.urls.controlled_list_item_image_add"
        :auto="true"
        :max-file-size="5e6"
        :file-limit="10"
        :preview-width="250"
        :with-credentials="true"
        name="item_image"
        @before-send="addHeader($event)"
        @upload="onUpload($event)"
    />
    <div class="images">
        <ImageEditor
            v-for="image in item.images"
            :key="image.id"
            :image="image"
        />
        <span
            v-if="!item.images.length"
            :style="{ fontSize: 'small'}"
        >
            {{ $gettext("No images.") }}
        </span>
    </div>
</template>

<style scoped>
h4 {
    color: v-bind(ARCHES_CHROME_BLUE);
    margin-top: 0;
    font-size: small;
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
</style>
