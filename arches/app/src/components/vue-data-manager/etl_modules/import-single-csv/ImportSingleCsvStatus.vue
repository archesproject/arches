<script setup>
import { useGettext } from "vue3-gettext";

const { $gettext } = useGettext();
const props = defineProps({selectedLoadEvent: {type: Object, default: () => {}}});

const emit = defineEmits(["getGraphName"]);

const emitGetGraphName = (graphId) => {
    emit("getGraphName", graphId);
};
</script>

<template>
    <div v-if="props.selectedLoadEvent">
        {{ props.selectedLoadEvent.load_details.file_name }}
        <div 
            class="bulk-load-status" 
            style="margin-bottom: 20px"
        >
            <h4 class="summary-title">
                <span 
                    v-text="$gettext('Import Single CSV Summary')"
                />
            </h4>
            <div>
                <span
                    class="etl-loading-metadata-key"
                    v-text="$gettext('File Name') + ':'"
                />
                <span
                    class="etl-loading-metadata-value"
                    v-text="props.selectedLoadEvent.load_details.file_name"
                />
            </div>
            <div>
                <span
                    class="etl-loading-metadata-key"
                    v-text="$gettext('Target Resource') + ':'"
                />
                <span
                    class="etl-loading-metadata-value"
                    v-text="
                        emitGetGraphName(
                            props.selectedLoadEvent.load_details.graph
                        )
                    "
                />
            </div>
        </div>
    </div>
</template>
