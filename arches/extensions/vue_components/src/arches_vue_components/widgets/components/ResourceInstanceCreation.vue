<script setup lang="ts">
import { ref, watchEffect } from "vue";

import Dialog from "openvue/dialog";
import Message from "openvue/message";

import { fetchGraph } from "@/arches_vue_components/datatypes/resource-instance-list/api.ts";

import GenericCard from "@/arches_vue_components/generics/GenericCard/GenericCard.vue";
import { EDIT } from "@/arches_vue_components/widgets/constants.ts";

import type {
    AliasedTileData,
    Card,
    Node,
    NodeGroup,
} from "@/arches_vue_components/types.ts";

const { graphId } = defineProps<{
    graphId: string;
}>();

const emit = defineEmits<{
    (event: "resourceCreated", resource: AliasedTileData): void;
}>();

const visible = ref(true);

const graphSlug = ref<string>("");
const graphName = ref<string>("");
const nodegroupAlias = ref<string>("");

watchEffect(async () => {
    visible.value = false;
    const graph = await fetchGraph(graphId);
    graphSlug.value = graph.graph.slug;
    graphName.value = graph.graph.name;
    const rootNodeGroupIds = graph.graph.nodegroups
        .filter((nodegroup: NodeGroup) => nodegroup.parentnodegroup_id === null)
        .map((nodegroup: NodeGroup) => nodegroup.nodegroupid);
    const card = graph.cards.find((card: Card) => {
        return (
            card.sortorder == 0 && rootNodeGroupIds.includes(card.nodegroup_id)
        );
    });
    nodegroupAlias.value = card.nodes.find(
        (node: Node) => node.nodeid === card.nodegroup_id,
    )?.alias;
    visible.value = true;
});

function onSave(event: AliasedTileData) {
    visible.value = false;
    emit("resourceCreated", event);
}
</script>

<template>
    <Dialog
        v-model:visible="visible"
        position="center"
        :draggable="false"
        :header="
            $gettext('Create a new %{graphName}', { graphName: graphName })
        "
        :close-on-escape="true"
        :modal="true"
        :pt="{
            root: {
                class: 'resource-instance-creation-dialog',
                style: {
                    width: '64rem',
                    maxWidth: 'calc(100vw - 3.2rem)',
                    borderRadius: '0',
                },
            },
            header: {
                style: {
                    background: 'var(--p-content-hover-background)',
                    color: 'var(--p-text-color)',
                    borderBottom: '0.1rem solid var(--p-content-border-color)',
                    borderRadius: '0',
                },
            },
        }"
    >
        <Message
            class="resource-instance-creation-note"
            severity="info"
            size="small"
            icon="pi pi-info-circle"
        >
            <strong>
                {{
                    $gettext("You're creating a new %{graphName}.", {
                        graphName: graphName,
                    })
                }}
            </strong>
            {{
                $gettext(
                    "Add the basic details here. When you save, the new record is created right away and added to the field you're editing. To add more information later, open the new record from its link in the report.",
                )
            }}
        </Message>
        <GenericCard
            :mode="EDIT"
            :nodegroup-alias="nodegroupAlias"
            :graph-slug="graphSlug"
            :resource-instance-id="undefined"
            @save="onSave($event)"
        />
    </Dialog>
</template>

<!-- Not scoped: the dialog is teleported to <body>, outside this component. -->
<style>
.resource-instance-creation-dialog {
    /* Text inputs otherwise round more than the selects beside them. */
    --p-inputtext-border-radius: var(--p-select-border-radius);
}

.resource-instance-creation-dialog .p-dialog-content {
    padding-block-start: 1.25rem;
}

.resource-instance-creation-dialog .resource-instance-creation-note {
    margin-block-end: 1.2rem;
    border-radius: 0.15rem;
}

.resource-instance-creation-dialog
    .resource-instance-creation-note
    .p-message-content {
    gap: 1.5rem;
}

/* The small Message sizes its own text and icon; match the field labels. */
.resource-instance-creation-dialog
    .resource-instance-creation-note
    .p-message-text {
    font-size: 1.25rem;
    line-height: 1.4;
}

.resource-instance-creation-dialog
    .resource-instance-creation-note
    .p-message-icon {
    font-size: 1.4rem;
}

.resource-instance-creation-dialog .p-dialog-content .card-name {
    margin-block-end: 0;
}

.resource-instance-creation-dialog .p-dialog-content .p-button {
    border-radius: 0.15rem;
}

/* Matches the report editor panel's field labels. */
.resource-instance-creation-dialog .p-dialog-content .widget-label {
    margin-block-end: 0.5rem;
    color: var(--p-text-muted-color);
    font-size: 1.25rem;
    font-weight: 600;
}
</style>
