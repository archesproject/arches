<script setup lang="ts">
import { onMounted, useTemplateRef, watch } from "vue";

import CodeMirror from "codemirror";
import "codemirror/lib/codemirror.css";
import "codemirror/mode/javascript/javascript.js";
import { useGettext } from "vue3-gettext";

import Message from "openvue/message";

import type { GeoJsonIssue } from "@/arches_vue_components/components/MapComponent/utils/geometry-import.ts";

const UPDATE_MODEL_VALUE_EVENT = "update:modelValue" as const;
const EDITOR_CHANGE_EVENT = "change";
const EDITOR_TAB_SIZE = 2;

const { modelValue, errors } = defineProps<{
    modelValue: string;
    errors: GeoJsonIssue[];
}>();

const emit = defineEmits<{
    (event: typeof UPDATE_MODEL_VALUE_EVENT, value: string): void;
}>();

const editorContainer = useTemplateRef<HTMLDivElement>("editorContainer");

const { $gettext } = useGettext();

let editor: ReturnType<typeof CodeMirror>;

watch(
    () => modelValue,
    (value) => {
        if (editor.getValue() !== value) {
            editor.setValue(value);
        }
    },
);

onMounted(() => {
    editor = CodeMirror(editorContainer.value, {
        value: modelValue,
        mode: { name: "javascript", json: true },
        lineNumbers: true,
        tabSize: EDITOR_TAB_SIZE,
        viewportMargin: Infinity,
        screenReaderLabel: $gettext("GeoJSON"),
    });
    editor.on(EDITOR_CHANGE_EVENT, emitEditorValue);
});

function emitEditorValue(): void {
    const value = editor.getValue();
    if (value !== modelValue) {
        emit(UPDATE_MODEL_VALUE_EVENT, value);
    }
}

function formatError(error: GeoJsonIssue): string {
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
        <div
            ref="editorContainer"
            class="geojson-code-editor"
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

.geojson-code-editor {
    overflow: hidden;
    border: 0.1rem solid var(--p-form-field-border-color);
    border-radius: var(--p-form-field-border-radius);
}

.geojson-code-editor:focus-within {
    border-color: var(--p-form-field-focus-border-color);
}

.geojson-code-editor :deep(.CodeMirror) {
    height: 25.6rem;
    background: var(--p-form-field-background);
    color: var(--p-form-field-color);
    font-size: 1.2rem;
}

.geojson-code-editor :deep(.CodeMirror-gutters) {
    border-inline-end-color: var(--p-form-field-border-color);
    background: var(--p-content-hover-background);
}

.geojson-code-editor :deep(.CodeMirror-linenumber) {
    color: var(--p-text-muted-color);
}

.geojson-code-editor :deep(.CodeMirror-cursor) {
    border-inline-start-color: var(--p-form-field-color);
}

.geojson-code-editor :deep(.CodeMirror-selected) {
    background: var(--p-highlight-background);
}

.geojson-code-editor :deep(.cm-string),
.geojson-code-editor :deep(.cm-atom) {
    color: var(--p-form-field-color);
}

.geojson-code-editor :deep(.cm-number) {
    color: var(--p-primary-color);
}

.geojson-code-editor :deep(.cm-property) {
    color: var(--p-text-muted-color);
}
</style>
