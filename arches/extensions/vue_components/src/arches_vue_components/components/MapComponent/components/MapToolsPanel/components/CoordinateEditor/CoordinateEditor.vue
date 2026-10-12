<script setup lang="ts">
import { computed, nextTick, ref, useId, useTemplateRef } from "vue";

import { useGettext } from "vue3-gettext";

import Button from "openvue/button";
import Message from "openvue/message";
import Select from "openvue/select";
import SelectButton from "openvue/selectbutton";

import GeoJsonTextEditor from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/components/GeoJsonTextEditor.vue";
import VertexTable from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/components/VertexTable.vue";
import ToolButtonGroup from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/ToolButtonGroup.vue";

import {
    GEOMETRY_ICON_BY_TYPE,
    POINT,
} from "@/arches_vue_components/components/MapComponent/constants.ts";
import { useDrawnFeatureLabels } from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/composables/useDrawnFeatureLabels.ts";
import { useGeometryKindOptions } from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/composables/useGeometryKindOptions.ts";
import { useResolvedMapContext } from "@/arches_vue_components/components/MapComponent/composables/useMapContext.ts";
import { useCoordinateEditor } from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/composables/useCoordinateEditor.ts";
import { useCoordinateGeoJsonText } from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/composables/useCoordinateGeoJsonText.ts";
import { useCoordinatePreview } from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/composables/useCoordinatePreview.ts";

import type { CoordinateRow } from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/types.ts";
import type {
    DrawMode,
    MapContext,
} from "@/arches_vue_components/components/MapComponent/types.ts";

const CLOSE_EVENT = "close" as const;

type DisplayMode = "vertices" | "geojson";

const { context = undefined, editingFeatureId = null } = defineProps<{
    context?: MapContext;
    editingFeatureId?: string | null;
}>();

const emit = defineEmits<{
    (event: typeof CLOSE_EVENT): void;
}>();

const vertexTable =
    useTemplateRef<InstanceType<typeof VertexTable>>("vertexTable");

const { $gettext } = useGettext();

const resolvedContext = useResolvedMapContext(context, "CoordinateEditor");
const { coordinateSystems, drawnFeatures, allowedGeometryTypes } =
    resolvedContext;
const kindOptions = useGeometryKindOptions(allowedGeometryTypes);
const labelsByFeatureId = useDrawnFeatureLabels(drawnFeatures);
const coordinateEditor = useCoordinateEditor(
    resolvedContext,
    editingFeatureId,
    kindOptions.value[0]?.value ?? POINT,
);
const {
    editingFeature,
    kind,
    srid,
    rows,
    errorMessage,
    canUndo,
    decimalPlaces,
    axisLabels,
    minimumVertices,
    previewGeometry,
    setKind,
    setSrid,
    updateRow,
    addRow,
    removeRow,
    commitRowEdit,
    undo,
    submit,
} = coordinateEditor;
const {
    geoJsonText,
    geoJsonErrors,
    resetGeoJsonText,
    updateGeoJsonText,
    flushGeoJsonText,
} = useCoordinateGeoJsonText(coordinateEditor);

const sridSelectId = useId();

const displayMode = ref<DisplayMode>("vertices");
const focusedRowIndex = ref<number | null>(null);

const {
    focusedRowPosition,
    followFocusedRow,
    followFocusedRowDebounced,
    fitToPreview,
} = useCoordinatePreview(resolvedContext, coordinateEditor, focusedRowIndex);

const displayModeOptions = [
    { value: "vertices", label: $gettext("Vertices"), icon: "pi pi-list" },
    { value: "geojson", label: $gettext("GeoJSON"), icon: "pi pi-code" },
];

const editingLabelHtml = computed(() => {
    if (editingFeatureId === null) {
        return "";
    }
    return $gettext("Editing <strong>%{label}</strong>", {
        label: labelsByFeatureId.value[editingFeatureId],
    });
});

const canCenter = computed(() => {
    if (displayMode.value === "vertices") {
        return focusedRowPosition.value !== null;
    }
    return previewGeometry.value !== null;
});

const modeLabels = computed(() => {
    if (displayMode.value === "vertices") {
        return {
            listHeader: $gettext("Vertices"),
            centerTitle: $gettext("Center map on the focused vertex"),
            undoTitle: $gettext("Undo the last vertex edit"),
        };
    }
    return {
        listHeader: $gettext("GeoJSON"),
        centerTitle: $gettext("Center map on this geometry"),
        undoTitle: $gettext("Undo the last edit"),
    };
});

const actionLabels = computed(() => {
    if (editingFeature) {
        return {
            cancel: $gettext("Cancel"),
            submit: $gettext("Update geometry"),
        };
    }
    return { cancel: $gettext("Done"), submit: $gettext("Add geometry") };
});

function selectKind(newKind: DrawMode): void {
    setKind(newKind);
    focusedRowIndex.value = null;
}

function setDisplayMode(mode: DisplayMode): void {
    if (mode === "geojson") {
        resetGeoJsonText();
    }
    displayMode.value = mode;
}

function handleRowUpdate(
    index: number,
    axis: keyof CoordinateRow,
    value: number | null,
): void {
    updateRow(index, axis, value);
    followFocusedRowDebounced();
}

function handleRowRemove(index: number): void {
    removeRow(index);
    if (focusedRowIndex.value !== null && focusedRowIndex.value >= index) {
        focusedRowIndex.value = null;
    }
}

async function handleAddRow(): Promise<void> {
    const insertedIndex = addRow(focusedRowIndex.value);
    focusedRowIndex.value = insertedIndex;
    await nextTick();
    vertexTable.value?.focusRow(insertedIndex);
}

function handleUndo(): void {
    undo();
    resetGeoJsonText();
}

function centerMap(): void {
    if (displayMode.value === "vertices" && focusedRowPosition.value) {
        followFocusedRow();
        return;
    }
    fitToPreview();
}

function handleSubmit(): void {
    if (displayMode.value === "geojson") {
        flushGeoJsonText();
        if (geoJsonErrors.value.length) {
            return;
        }
    }

    const shouldClose = submit();
    if (shouldClose) {
        emit(CLOSE_EVENT);
        return;
    }
    focusedRowIndex.value = null;
    displayMode.value = "vertices";
}
</script>

<template>
    <div class="coordinate-editor">
        <div class="coordinate-editor-section">
            <template v-if="!editingFeature && displayMode === 'vertices'">
                <span class="coordinate-editor-label">
                    {{ $gettext("Geometry type") }}
                </span>
                <ToolButtonGroup
                    :options="kindOptions"
                    :active-value="kind"
                    @select="selectKind"
                />
            </template>
            <div
                v-if="editingFeature"
                class="coordinate-editor-editing"
            >
                <i
                    aria-hidden="true"
                    :class="GEOMETRY_ICON_BY_TYPE[editingFeature.geometry.type]"
                />
                <!-- eslint-disable vue/no-v-html -->
                <span v-html="editingLabelHtml" />
                <!-- eslint-enable vue/no-v-html -->
            </div>
            <SelectButton
                class="coordinate-editor-mode-toggle"
                option-label="label"
                option-value="value"
                :model-value="displayMode"
                :options="displayModeOptions"
                :allow-empty="false"
                :aria-label="$gettext('Coordinate display mode')"
                @update:model-value="setDisplayMode"
            >
                <template #option="{ option }">
                    <i
                        aria-hidden="true"
                        :class="option.icon"
                    />
                    <span>{{ option.label }}</span>
                </template>
            </SelectButton>
            <template v-if="displayMode === 'vertices'">
                <label
                    class="coordinate-editor-label"
                    :for="sridSelectId"
                >
                    {{ $gettext("Spatial reference system") }}
                </label>
                <Select
                    option-label="name"
                    option-value="srid"
                    append-to="self"
                    size="small"
                    :model-value="srid"
                    :input-id="sridSelectId"
                    :options="coordinateSystems"
                    :fluid="true"
                    @update:model-value="setSrid"
                />
            </template>
        </div>

        <div class="coordinate-editor-section coordinate-editor-scroll-section">
            <div class="coordinate-editor-list-header">
                <span class="coordinate-editor-label">
                    {{ modeLabels.listHeader }}
                </span>
                <div class="coordinate-editor-list-actions">
                    <Button
                        icon="pi pi-search-plus"
                        size="small"
                        :title="modeLabels.centerTitle"
                        :label="$gettext('Center')"
                        :link="true"
                        :disabled="!canCenter"
                        @click="centerMap"
                    />
                    <Button
                        icon="pi pi-undo"
                        size="small"
                        :title="modeLabels.undoTitle"
                        :label="$gettext('Undo')"
                        :link="true"
                        :disabled="!canUndo"
                        @click="handleUndo"
                    />
                </div>
            </div>
            <template v-if="displayMode === 'vertices'">
                <VertexTable
                    ref="vertexTable"
                    :rows="rows"
                    :axis-labels="axisLabels"
                    :decimal-places="decimalPlaces"
                    :minimum-vertices="minimumVertices"
                    :highlighted-row-index="focusedRowIndex"
                    @update-row="handleRowUpdate"
                    @focus-row="focusedRowIndex = $event"
                    @blur-row="commitRowEdit"
                    @remove-row="handleRowRemove"
                />
                <Button
                    v-if="kind !== 'point'"
                    class="coordinate-editor-add-vertex"
                    icon="pi pi-plus"
                    size="small"
                    :label="$gettext('Add vertex')"
                    :link="true"
                    @click="handleAddRow"
                />
                <Message
                    v-if="errorMessage"
                    severity="error"
                    size="small"
                    role="alert"
                >
                    {{ errorMessage }}
                </Message>
            </template>
            <GeoJsonTextEditor
                v-else
                :model-value="geoJsonText"
                :errors="geoJsonErrors"
                @update:model-value="updateGeoJsonText"
            />
        </div>

        <div class="coordinate-editor-actions">
            <Button
                size="small"
                :label="actionLabels.cancel"
                :link="true"
                @click="emit(CLOSE_EVENT)"
            />
            <Button
                size="small"
                :label="actionLabels.submit"
                @click="handleSubmit"
            />
        </div>
    </div>
</template>

<style scoped>
.coordinate-editor {
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 0;
}

.coordinate-editor-section {
    display: flex;
    flex: 0 0 auto;
    flex-direction: column;
    gap: 0.8rem;
    padding-block: 1.1rem;
    padding-inline: 1.3rem;
    border-block-end: 0.1rem solid var(--p-content-border-color);
}

.coordinate-editor-scroll-section {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    border-block-end: none;
}

.coordinate-editor-label {
    margin: 0;
    color: var(--p-text-muted-color);
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 0.06rem;
    text-transform: uppercase;
}

.coordinate-editor-editing {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    font-size: 1.35rem;
    font-weight: 600;
}

.coordinate-editor-editing .pi {
    color: var(--p-primary-color);
}

.coordinate-editor-mode-toggle {
    display: flex;
}

.coordinate-editor-mode-toggle :deep(.p-togglebutton) {
    flex: 1;
    gap: 0.5rem;
    font-size: 1.2rem;
}

.coordinate-editor-list-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.8rem;
}

.coordinate-editor-list-actions {
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

.coordinate-editor-add-vertex {
    align-self: flex-start;
}

.coordinate-editor-actions {
    display: flex;
    flex: 0 0 auto;
    align-items: center;
    justify-content: space-between;
    gap: 0.8rem;
    padding-block: 1.1rem;
    padding-inline: 1.3rem;
    border-block-start: 0.1rem solid var(--p-content-border-color);
}
</style>
