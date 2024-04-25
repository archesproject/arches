<script setup lang="ts">
import arches from "arches";
import { useGettext } from "vue3-gettext";

import type { ReferencingNode } from "@/types/ControlledListManager";

const props: { node: ReferencingNode } = defineProps(["node"]);

const { $gettext } = useGettext();
</script>

<template>
    <span class="referencing-node">
        {{ $gettext(
            "%{ graphName }: %{ nodeName }",
            { graphName: props.node.graph_name, nodeName: props.node.name, }
        )
        }}
        <a
            :href="arches.urls.graph_designer(node.graph_id)"
            target="_blank"
        >
            <i
                class="fa fa-reply"
                aria-hidden="true"
            />
            {{ $gettext("Edit graph") }}
        </a>
    </span>
</template>

<style scoped>
.referencing-node {
    display: inline-flex;
    padding: 1rem;
    gap: 2rem;
    align-items: center;
    font-size: small;
    text-align: center;
    border-radius: 2px;
    height: 3rem;
    background: var(--gray-200);
    text-wrap: nowrap;
}
</style>
