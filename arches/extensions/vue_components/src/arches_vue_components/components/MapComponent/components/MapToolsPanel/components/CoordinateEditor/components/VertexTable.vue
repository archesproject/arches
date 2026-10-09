<script setup lang="ts">
import { useId } from "vue";

import { useGettext } from "vue3-gettext";

import Button from "openvue/button";
import InputNumber from "openvue/inputnumber";

import type { CoordinateRow } from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/types.ts";

const UPDATE_ROW_EVENT = "update-row" as const;
const FOCUS_ROW_EVENT = "focus-row" as const;
const BLUR_ROW_EVENT = "blur-row" as const;
const REMOVE_ROW_EVENT = "remove-row" as const;
const AXES = ["x", "y"] as const;

const {
    rows,
    axisLabels,
    decimalPlaces,
    minimumVertices,
    highlightedRowIndex,
} = defineProps<{
    rows: CoordinateRow[];
    axisLabels: { x: string; y: string };
    decimalPlaces: number;
    minimumVertices: number;
    highlightedRowIndex: number | null;
}>();

const emit = defineEmits<{
    (
        event: typeof UPDATE_ROW_EVENT,
        index: number,
        axis: keyof CoordinateRow,
        value: number | null,
    ): void;
    (event: typeof FOCUS_ROW_EVENT, index: number): void;
    (event: typeof BLUR_ROW_EVENT, index: number): void;
    (event: typeof REMOVE_ROW_EVENT, index: number): void;
}>();

defineExpose({ focusRow });

const { $gettext } = useGettext();

const idPrefix = useId();

function getInputId(index: number, axis: keyof CoordinateRow): string {
    return `${idPrefix}-${axis}-${index}`;
}

function focusRow(index: number): void {
    document.getElementById(getInputId(index, "x"))?.focus();
}
</script>

<template>
    <div class="vertex-table">
        <div
            v-for="(row, index) in rows"
            :key="index"
            class="vertex-row"
            :class="{ 'vertex-row-highlighted': index === highlightedRowIndex }"
        >
            <span class="vertex-index">{{ index + 1 }}</span>
            <InputNumber
                v-for="axis in AXES"
                :key="axis"
                class="vertex-input"
                size="small"
                :model-value="row[axis]"
                :input-id="getInputId(index, axis)"
                :placeholder="axisLabels[axis]"
                :aria-label="
                    $gettext('%{axis} for vertex %{number}', {
                        axis: axisLabels[axis],
                        number: String(index + 1),
                    })
                "
                :use-grouping="false"
                :min-fraction-digits="0"
                :max-fraction-digits="decimalPlaces"
                :fluid="true"
                @update:model-value="
                    emit(UPDATE_ROW_EVENT, index, axis, $event)
                "
                @focus="emit(FOCUS_ROW_EVENT, index)"
                @blur="emit(BLUR_ROW_EVENT, index)"
            />
            <Button
                v-if="rows.length > minimumVertices"
                icon="pi pi-trash"
                :title="$gettext('Remove vertex')"
                severity="secondary"
                size="small"
                :aria-label="
                    $gettext('Remove vertex %{number}', {
                        number: String(index + 1),
                    })
                "
                @click="emit(REMOVE_ROW_EVENT, index)"
            />
        </div>
    </div>
</template>

<style scoped>
.vertex-table {
    display: flex;
    flex-direction: column;
    gap: 0.65rem;
}

.vertex-row {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    padding: 0.25rem;
    border-radius: 0.5rem;
}

.vertex-row-highlighted {
    background: var(--p-highlight-background);
}

.vertex-index {
    flex: 0 0 auto;
    width: 1.75rem;
    color: var(--p-text-muted-color);
    font-size: 1.15rem;
    text-align: end;
}

.vertex-row-highlighted .vertex-index {
    color: var(--p-primary-color);
    font-weight: 700;
}

.vertex-input {
    flex: 1;
    min-width: 0;
}
</style>
