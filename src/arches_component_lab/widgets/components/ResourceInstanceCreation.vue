<script setup lang="ts">
import { ref, watchEffect } from "vue";

import Dialog from "primevue/dialog";

import { fetchGraph } from "@/arches_component_lab/datatypes/resource-instance-list/api.ts";

import GenericCard from "@/arches_component_lab/generics/GenericCard/GenericCard.vue";
import { EDIT } from "@/arches_component_lab/widgets/constants.ts";

import type {
    AliasedTileData,
    Card,
    Node,
    NodeGroup,
} from "@/arches_component_lab/types.ts";

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
                style: {
                    borderRadius: '0',
                },
            },
            header: {
                style: {
                    background: 'var(--p-navigation-header-color)',
                    color: 'var(--p-dialog-header-text-color)',
                    borderRadius: '0',
                },
            },
        }"
    >
        <GenericCard
            :mode="EDIT"
            :nodegroup-alias="nodegroupAlias"
            :graph-slug="graphSlug"
            :resource-instance-id="undefined"
            @save="onSave($event)"
        />
    </Dialog>
</template>

<style scoped></style>
