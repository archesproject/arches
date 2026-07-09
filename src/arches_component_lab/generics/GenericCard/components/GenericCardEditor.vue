<script setup lang="ts">
import {
    reactive,
    toRaw,
    ref,
    watch,
    nextTick,
    useTemplateRef,
    computed,
} from "vue";
import { useGettext } from "vue3-gettext";

import { Form } from "@primevue/forms";
import Button from "primevue/button";
import Message from "primevue/message";
import Skeleton from "primevue/skeleton";

import GenericWidget from "@/arches_component_lab/generics/GenericWidget/GenericWidget.vue";
import { upsertTile } from "@/arches_component_lab/generics/GenericCard/api.ts";
import {
    deepClone,
    extractAliasedNodeDataEntries,
} from "@/arches_component_lab/generics/GenericCard/utils.ts";
import { EDIT } from "@/arches_component_lab/widgets/constants.ts";

import type {
    AliasedData,
    AliasedNodeData,
    AliasedTileData,
    CardXNodeXWidgetData,
} from "@/arches_component_lab/types.ts";

const {
    cardXNodeXWidgetData,
    graphSlug,
    nodegroupAlias,
    resourceInstanceId,
    selectedNodeAlias,
    shouldShowFormButtons = true,
    tileData,
} = defineProps<{
    cardXNodeXWidgetData: CardXNodeXWidgetData[];
    graphSlug: string;
    nodegroupAlias: string;
    resourceInstanceId: string | null | undefined;
    selectedNodeAlias?: string | null;
    shouldShowFormButtons: boolean | undefined;
    tileData?: AliasedTileData;
}>();

const emit = defineEmits([
    "update:tileData",
    "update:widgetDirtyStates",
    "update:widgetFocusStates",
    "save",
    "reset",
    "initialized",
]);

defineOptions({ inheritAttrs: false });
defineExpose({ save });

const { $gettext } = useGettext();

const genericWidgetRefs = useTemplateRef("genericWidget");

const formKey = ref(0);
const isSaving = ref(false);
const saveError = ref<Error>();

const originalAliasedNodeDataMap = deepClone(
    extractAliasedNodeDataEntries(
        (tileData?.aliased_data as Record<string, unknown>) || {},
    ),
);
const aliasedNodeDataMap = reactive<Record<string, AliasedNodeData>>(
    deepClone(originalAliasedNodeDataMap),
);

const localWidgetDirtyStates = reactive(
    cardXNodeXWidgetData.reduce<Record<string, boolean>>(
        (dirtyStatesMap, widgetDatum) => {
            dirtyStatesMap[widgetDatum.node.alias] = false;
            return dirtyStatesMap;
        },
        {},
    ),
);

const localWidgetFocusedStates = reactive(
    cardXNodeXWidgetData.reduce<Record<string, boolean>>(
        (focusedStatesMap, widgetDatum) => {
            focusedStatesMap[widgetDatum.node.alias] = false;
            return focusedStatesMap;
        },
        {},
    ),
);

const initializedNodeAliases = new Set<string>();
const initializedNodeData: Record<string, AliasedNodeData> = {};

const areButtonsDisabled = computed(() => {
    return Object.values(localWidgetDirtyStates).every(
        (isWidgetDirty) => !isWidgetDirty,
    );
});

watch(
    () => selectedNodeAlias,
    async (nodeAlias) => {
        if (!nodeAlias) {
            return;
        }

        await nextTick();
        await focusWidgetInputForNodeAlias(nodeAlias);
    },
    { immediate: true, flush: "post" },
);

watch(
    aliasedNodeDataMap,
    () => {
        emit("update:tileData", {
            ...tileData,
            aliased_data: toRaw(aliasedNodeDataMap) as AliasedData,
        });
    },
    { deep: true },
);

watch(
    () => ({ ...localWidgetDirtyStates }),
    (newDirtyStatesMap) => {
        emit("update:widgetDirtyStates", newDirtyStatesMap);
    },
);

watch(
    () => ({ ...localWidgetFocusedStates }),
    (newFocusedStatesMap) => {
        emit("update:widgetFocusStates", newFocusedStatesMap);
    },
);

function onUpdateWidgetDirtyState(nodeAlias: string, isDirty: boolean) {
    localWidgetDirtyStates[nodeAlias] = isDirty;
}

function onUpdateWidgetFocusedState(nodeAlias: string, isFocused: boolean) {
    localWidgetFocusedStates[nodeAlias] = isFocused;
}

function resetWidgetDirtyStates() {
    Object.keys(localWidgetDirtyStates).forEach((nodeAlias) => {
        localWidgetDirtyStates[nodeAlias] = false;
    });
}

function resetForm() {
    resetWidgetDirtyStates();

    const originalAliasedNodeDataMapClone = deepClone(
        originalAliasedNodeDataMap,
    );
    Object.assign(aliasedNodeDataMap, originalAliasedNodeDataMapClone);
    formKey.value += 1;

    nextTick(() => {
        emit("reset", originalAliasedNodeDataMapClone);
    });
}

async function save() {
    isSaving.value = true;
    saveError.value = undefined;

    try {
        const updatedTileData = await upsertTile(
            graphSlug,
            nodegroupAlias,
            {
                ...(tileData as AliasedTileData),
                aliased_data: toRaw(
                    aliasedNodeDataMap,
                ) as AliasedTileData["aliased_data"],
            },
            tileData?.tileid ? tileData.tileid : undefined,
            resourceInstanceId,
        );

        const freshAliasedNodeDataMap = extractAliasedNodeDataEntries(
            updatedTileData.aliased_data as Record<string, unknown>,
        );
        Object.assign(aliasedNodeDataMap, deepClone(freshAliasedNodeDataMap));
        Object.assign(
            originalAliasedNodeDataMap,
            deepClone(freshAliasedNodeDataMap),
        );

        resetWidgetDirtyStates();

        nextTick(() => {
            emit("save", updatedTileData);
        });
    } catch (caughtError) {
        saveError.value = caughtError as Error;
    } finally {
        isSaving.value = false;
    }
}

async function focusWidgetInputForNodeAlias(nodeAlias: string) {
    for (let attemptCount = 0; attemptCount < 5; attemptCount += 1) {
        const widgetComponentRefs = genericWidgetRefs.value;
        if (!Array.isArray(widgetComponentRefs)) {
            return;
        }

        const activeElement = document.activeElement as HTMLElement | null;

        for (const widgetComponentRef of widgetComponentRefs) {
            const widgetRootElement =
                widgetComponentRef?.$el as HTMLElement | null;

            if (!widgetRootElement) {
                continue;
            }

            if (activeElement && widgetRootElement.contains(activeElement)) {
                return;
            }

            const inputElementToFocus =
                widgetRootElement.querySelector<HTMLElement>(
                    `[id="${nodeAlias}"]`,
                );

            if (inputElementToFocus) {
                inputElementToFocus.focus();
                return;
            }
        }

        await new Promise<void>((resolve) => {
            requestAnimationFrame(() => resolve());
        });
    }
}

function onWidgetInitialized(
    nodeAlias: string,
    aliasedNodeData: AliasedNodeData,
) {
    initializedNodeData[nodeAlias] = aliasedNodeData;
    initializedNodeAliases.add(nodeAlias);

    const allVisibleWidgetsInitialized = cardXNodeXWidgetData
        .filter((datum) => datum.visible)
        .every((datum) => initializedNodeAliases.has(datum.node.alias));

    if (allVisibleWidgetsInitialized) {
        emit("initialized", initializedNodeData);
    }
}

function onUpdateWidgetAliasedNodeData(
    nodeAlias: string,
    nodeData: AliasedNodeData,
) {
    aliasedNodeDataMap[nodeAlias] = nodeData;
}
</script>

<template>
    <Skeleton
        v-if="isSaving"
        style="height: 10rem"
    />
    <template v-else>
        <Message
            v-if="saveError"
            severity="error"
        >
            {{ saveError.message }}
        </Message>
        <Form
            :key="formKey"
            class="form"
        >
            <template
                v-for="cardXNodeXWidgetDatum in cardXNodeXWidgetData"
                :key="cardXNodeXWidgetDatum.id"
            >
                <GenericWidget
                    v-if="cardXNodeXWidgetDatum.visible"
                    v-bind="$attrs"
                    ref="genericWidget"
                    :aliased-node-data="
                        aliasedNodeDataMap[cardXNodeXWidgetDatum.node.alias] ??
                        null
                    "
                    :is-dirty="
                        localWidgetDirtyStates[cardXNodeXWidgetDatum.node.alias]
                    "
                    :card-x-node-x-widget-data="cardXNodeXWidgetDatum"
                    :graph-slug="graphSlug"
                    :mode="EDIT"
                    :node-alias="cardXNodeXWidgetDatum.node.alias"
                    :value="
                        aliasedNodeDataMap[cardXNodeXWidgetDatum.node.alias]
                            ?.node_value ?? null
                    "
                    @update:aliased-node-data="
                        onUpdateWidgetAliasedNodeData(
                            cardXNodeXWidgetDatum.node.alias,
                            $event,
                        )
                    "
                    @update:is-dirty="
                        onUpdateWidgetDirtyState(
                            cardXNodeXWidgetDatum.node.alias,
                            $event,
                        )
                    "
                    @update:is-focused="
                        onUpdateWidgetFocusedState(
                            cardXNodeXWidgetDatum.node.alias,
                            $event,
                        )
                    "
                    @initialized="
                        onWidgetInitialized(
                            cardXNodeXWidgetDatum.node.alias,
                            $event,
                        )
                    "
                />
            </template>

            <div
                v-if="shouldShowFormButtons"
                class="form-action-buttons"
            >
                <Button
                    :disabled="areButtonsDisabled"
                    :loading="isSaving"
                    severity="success"
                    size="small"
                    icon="pi pi-check"
                    :label="$gettext('Save')"
                    @click="save"
                />
                <Button
                    :disabled="areButtonsDisabled"
                    type="button"
                    severity="warn"
                    size="small"
                    icon="pi pi-undo"
                    :label="$gettext('Cancel')"
                    @click="resetForm"
                />
            </div>
        </Form>
    </template>
</template>

<style scoped>
.form {
    display: flex;
    flex-direction: column;
    gap: 1.4rem;
}

.form-action-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    padding-top: 1rem;
    flex-wrap: wrap;
}
</style>
