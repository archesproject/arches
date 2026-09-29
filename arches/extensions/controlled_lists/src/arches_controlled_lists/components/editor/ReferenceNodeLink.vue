<script setup lang="ts">
import arches from "arches";
import { useGettext } from "vue3-gettext";

import type { ReferencingNode } from "@/arches_controlled_lists/types";

const props = defineProps<{ node: ReferencingNode }>();

const { $gettext } = useGettext();
</script>

<template>
    <span class="referencing-node">
        {{
            $gettext("%{graphName}: %{nodeName}", {
                graphName: props.node.graph_name,
                nodeName: props.node.name,
            })
        }}<a
            :href="arches.urls.graph_designer(node.graph_id)"
            target="_blank"
            style="text-decoration: underline; color: var(--p-content-color)"
        >
            <i
                class="fa fa-reply"
                aria-hidden="true"
                style="margin: 0.5rem"
            />{{ $gettext("Edit graph") }}
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
    border-radius: var(--p-content-border-radius);
    height: 3rem;
    background: var(--p-content-hover-background);
    text-wrap: nowrap;
}
</style>
