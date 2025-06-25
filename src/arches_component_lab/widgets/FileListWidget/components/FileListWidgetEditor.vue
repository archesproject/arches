<script setup lang="ts">
import { onMounted, useTemplateRef, ref, computed } from "vue";
import { useGettext } from "vue3-gettext";

import Message from "primevue/message";
import FileUpload from "primevue/fileupload";
import Image from "primevue/image";
import Button from "primevue/button";
import { FormField } from "@primevue/forms";
import type {
    FileUploadRemoveEvent,
    FileUploadSelectEvent,
} from "primevue/fileupload";
import type { FormFieldResolverOptions } from "@primevue/forms";
import type { FileReference } from "@/arches_component_lab/widgets/types.ts";

const { $gettext } = useGettext();
const allowedFileTypes = ref();
const props = defineProps<{
    initialValue: FileReference[] | null | undefined;
    graphSlug: string;
    nodeAlias: string;
    widgetData: {
        config: {
            acceptedFiles: string;
            maxFilesize: number;
            rerender: boolean;
            label: string;
        };
    };
    nodeData: {
        config: {
            imagesOnly: boolean;
            maxFiles: number;
            maxFileSize: number;
        };
    };
}>();

const formFieldRef = useTemplateRef("formFieldRef");
const currentValues = ref<FileReference[]>();

onMounted(() => {
    const acceptedFiles = props.widgetData.config.acceptedFiles;
    allowedFileTypes.value = acceptedFiles != "" ? acceptedFiles : null;

    if (props.initialValue) {
        currentValues.value = props.initialValue;
    }
});

const currentMax = computed(() => {
    if (currentValues.value) {
        return (
            props.nodeData.config.maxFiles - (currentValues.value.length ?? 0)
        );
    } else {
        return props.nodeData.config.maxFiles;
    }
});

function resolver(e: FormFieldResolverOptions) {
    validate(e);
}

function select(event: FileUploadSelectEvent) {
    // @ts-expect-error - This is a bug in the PrimeVue types
    formFieldRef.value!.field.states.value = {
        // @ts-expect-error - This is a bug in the PrimeVue types
        ...(formFieldRef.value!.field.states.value ?? {}),
        newFiles: event.files,
    };
}

function remove(event: FileUploadRemoveEvent) {
    // @ts-expect-error - This is a bug in the PrimeVue types
    formFieldRef.value!.field.states.value = {
        // @ts-expect-error - This is a bug in the PrimeVue types
        ...(formFieldRef.value!.field.states.value ?? {}),
        newFiles: event.files,
    };
}

function validate(e: FormFieldResolverOptions) {
    console.log("validate", e);
}

function deleteImage(fileId: string) {
    // @ts-expect-error - This is a bug in the PrimeVue types
    formFieldRef.value!.field.states.value = {
        // @ts-expect-error - This is a bug in the PrimeVue types
        ...(formFieldRef.value!.field.states.value ?? {}),
        deletedFiles: [
            // @ts-expect-error - This is a bug in the PrimeVue types
            ...(formFieldRef.value!.field.states.value?.deletedFiles ?? []),
            fileId,
        ],
    };
    if (currentValues.value) {
        const fileIndex = currentValues.value
            .map((image) => image.file_id)
            .indexOf(fileId);

        if (fileIndex != -1) {
            currentValues.value?.splice(fileIndex, 1);
        }
    }
}
</script>

<template>
    <FormField
        ref="formFieldRef"
        v-slot="$field"
        :name="props.nodeAlias"
        :initial-value="props.initialValue"
        :resolver="resolver"
    >
        <div class="uploaded-images-container">
            <div
                v-for="image in currentValues"
                :key="image.file_id"
                class="uploaded-image-row"
            >
                <Image
                    :key="image.file_id"
                    class="uploaded-image"
                    :src="image.url"
                    :alt="image.name"
                ></Image>
                <Button
                    icon="pi pi-trash"
                    :aria-label="$gettext('delete')"
                    severity="danger"
                    @click="deleteImage(image.file_id)"
                />
            </div>
        </div>
        <FileUpload
            :accept="allowedFileTypes"
            :file-limit="currentMax"
            :disabled="currentMax == 0"
            :preview-width="250"
            :with-credentials="true"
            :show-cancel-button="false"
            :show-upload-button="false"
            choose-icon="fa fa-plus-circle"
            :choose-label="$gettext('Upload an image')"
            :name="props.nodeAlias"
            @select="select"
            @remove="remove"
        >
        </FileUpload>
        <Message
            v-for="error in $field.errors"
            :key="error.message"
            severity="error"
            size="small"
        >
            {{ error.message }}
        </Message>
    </FormField>
</template>
<style scoped>
.uploaded-images-container {
    display: flex;
}

:deep(.uploaded-image img) {
    width: 100%;
    height: auto;
    max-width: 12rem;
}

:deep(.uploaded-image-row) {
    display: flex;
}
</style>
