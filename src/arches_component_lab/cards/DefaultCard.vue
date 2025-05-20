<script setup lang="ts">
import { ref, watchEffect } from "vue";

import Message from "primevue/message";
import ProgressSpinner from "primevue/progressspinner";

import { fetchCardData } from "@/arches_component_lab/cards/api.ts";
import { fetchWidgetDataFromCard } from "@/arches_component_lab/widgets/api.ts";

const props = defineProps<{
    nodeAlias: string;
    graphSlug: string;
}>();

const isLoading = ref();
const cardData = ref();
const widgetData = ref();
const configurationError = ref();

watchEffect(async () => {
    isLoading.value = true;

    try {
        cardData.value = await fetchCardData(
            props.graphSlug, 
            props.nodeAlias,
        );
        widgetData.value = await fetchWidgetDataFromCard(
            props.graphSlug,
            props.nodeAlias,
        );
    } catch (error) {
        configurationError.value = error;
    } finally {
        isLoading.value = false;
    }
});
</script>
<template>
    <ProgressSpinner
        v-if="isLoading"
        style="width: 2em; height: 2em"
    />
    <div>HELLO</div>
    <Message
        v-if="configurationError"
        severity="error"
    >
        {{ configurationError.message }}
    </Message>
</template>
<style scoped>

</style>