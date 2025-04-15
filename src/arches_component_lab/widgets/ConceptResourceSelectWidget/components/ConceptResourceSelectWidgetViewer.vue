<script setup lang="ts">
import arches from "arches";
import { getItemLabel } from "@/arches_vue_utils/utils.ts";
import { getParentLabels } from "@/arches_lingo/utils.ts";
import { ENGLISH } from "@/arches_lingo/constants.ts";
import type { SearchResultItem } from "@/arches_lingo/types.ts";

const props = defineProps<{
    value?: SearchResultItem[];
}>();
</script>
<template>
    <div
        v-for="searchResult in props.value"
        :key="searchResult.id"
    >
        <span>
            <a :href="`${arches.urls.resource_editor}${searchResult.id}`">
                {{
                    getItemLabel(searchResult, ENGLISH.code, ENGLISH.code).value
                }}
            </a>
        </span>
        <span class="concept-hierarchy">
            [
            {{ getParentLabels(searchResult, ENGLISH.code, ENGLISH.code) }}
            ]
        </span>
    </div>
</template>
<style scoped>
.concept-hierarchy {
    font-size: small;
    color: steelblue;
}
</style>
