<script setup lang="ts">
import { useGettext } from "vue3-gettext";

import Message from "openvue/message";
import Textarea from "openvue/textarea";

import type { GeoJsonError } from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/types.ts";

const UPDATE_MODEL_VALUE_EVENT = "update:modelValue" as const;
const TEXTAREA_ROWS = 14;

const { modelValue, errors } = defineProps<{
    modelValue: string;
    errors: GeoJsonError[];
}>();

const emit = defineEmits<{
    (event: typeof UPDATE_MODEL_VALUE_EVENT, value: string): void;
}>();

const { $gettext } = useGettext();

function formatError(error: GeoJsonError): string {
    if (error.line === undefined) {
        return error.message;
    }
    return $gettext("Line %{line}: %{message}", {
        line: String(error.line),
        message: error.message,
    });
}
</script>

<template>
    <div class="geojson-text-editor">
        <Textarea
            class="geojson-textarea"
            spellcheck="false"
            :model-value="modelValue"
            :rows="TEXTAREA_ROWS"
            :aria-label="$gettext('GeoJSON')"
            :fluid="true"
            @update:model-value="emit(UPDATE_MODEL_VALUE_EVENT, $event ?? '')"
        />
        <Message
            v-if="errors.length"
            severity="error"
            size="small"
            role="alert"
        >
            <div
                v-for="(error, index) in errors"
                :key="index"
            >
                {{ formatError(error) }}
            </div>
        </Message>
    </div>
</template>

<style scoped>
.geojson-text-editor {
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
}

.geojson-textarea {
    font-family: monospace;
    font-size: 1.2rem;
    resize: vertical;
}
</style>
