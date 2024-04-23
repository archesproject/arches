<script setup>
import { useGettext } from "vue3-gettext";

const { $gettext } = useGettext();
const props = defineProps(["selectedLoadEvent"]);

const emit = defineEmits(["getGraphName"]);

const emitGetGraphName = (graphId) => {
    emit("getGraphName", graphId);
};
</script>

<template>
    <div v-if="props.selectedLoadEvent">
        {{ props.selectedLoadEvent.load_details.file_name }}
        <div class="bulk-load-status" style="margin-bottom: 20px">
            <h4 class="summary-title">
                <span v-text="$gettext('Import Single CSV Summary')"></span>
            </h4>
            <div>
                <span
                    class="etl-loading-metadata-key"
                    v-text="$gettext('File Name') + ':'"
                ></span>
                <span
                    class="etl-loading-metadata-value"
                    v-text="props.selectedLoadEvent.load_details.file_name"
                ></span>
            </div>
            <div>
                <span
                    class="etl-loading-metadata-key"
                    v-text="$gettext('Target Resource') + ':'"
                ></span>
                <span
                    class="etl-loading-metadata-value"
                    v-text="
                        emitGetGraphName(
                            props.selectedLoadEvent.load_details.graph
                        )
                    "
                ></span>
            </div>
        </div>
    </div>
</template>
