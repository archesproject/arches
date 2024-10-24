<script setup>
import { ref } from "vue";
import { useGettext } from "vue3-gettext";
import Splitter from "primevue/splitter";
import InputText from "primevue/inputtext";
import Paginator from "primevue/paginator";
import SplitterPanel from "primevue/splitterpanel";

const search = ref();
const { $gettext } = useGettext();
const emit = defineEmits([
    "reverseTransactions",
    "cleanLoadEvent",
    "stopEtl",
    "updateSelectedLoadEvent",
]);
const { loadEvents } = defineProps({loadEvents: {type: Array, default: () => []}});

const formatTime = (timeString) => {
    if (timeString) {
        const timeObject = new Date(timeString);
        return timeObject.toLocaleString();
    } else {
        return null;
    }
};

const formatUserName = (event) => {
    if (event.first_name || event.last_name) {
        return [event.first_name, event.last_name].join(" ");
    } else {
        return event.username;
    }
};

const emitReversedTransaction = (event, warningTitle, warningMessage) => {
    emit("reverseTransactions", event, warningTitle, warningMessage);
};

const emitCleanLoadEvent = (loadid) => {
    emit("cleanLoadEvent", loadid);
};

const emitStopEtl = (loadid) => {
    emit("stopEtl", loadid);
};

const emitSelectedLoadEvent = (event) => {
    emit("updateSelectedLoadEvent", event);
};
</script>

<template>
    <div class="task-status">
        <div class="status-panel">
            <Splitter 
                style="height: 85vh"
                class="mb-5 job-list"
            >
                <SplitterPanel
                    class="flex align-items-center justify-content-center task-list"
                >
                    <div class="task-list-search-box">
                        <span class="p-input-icon-left">
                            <i class="pi pi-search" />
                            <InputText
                                v-model.trim="search"
                                :placeholder="$gettext('Filter Tasks...')"
                            />
                        </span>
                    </div>
                    <div class="etl-jobs-container">
                        <div
                            v-for="(event, index) in loadEvents" 
                            :key="index"
                            class="etl-job"
                        >
                            <div
                                class="etl-job-metadata"
                                style="
                                    padding: 10px 15px;
                                    flex-direction: column;
                                    justify-content: space-between;
                                    cursor: pointer;
                                    height: 85px;
                                "
                                @click="emitSelectedLoadEvent(event)"
                            >
                                <div>
                                    <div
                                        style="
                                            font-size: 15px;
                                            color: rgb(4, 4, 45);
                                        "
                                    >
                                        {{ event.etl_module.name }}
                                    </div>
                                </div>
                                <div
                                    style="
                                        display: flex;
                                        flex-direction: row;
                                        justify-content: space-between;
                                    "
                                >
                                    <div>
                                        <div>
                                            {{ formatUserName(event.user) }}
                                        </div>
                                        <div>
                                            <span>start: </span>
                                            <span>{{
                                                formatTime(
                                                    event.load_start_time
                                                )
                                            }}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="etl-job-task-bar">
                                <div class="task">
                                    <a
                                        v-if="
                                            (event.status == 'completed' ||
                                                event.status == 'indexed') &&
                                                event.etl_module.reversible
                                        "
                                        @click="
                                            emitReversedTransaction(
                                                event,
                                                'Warning',
                                                'Are you sure you want to delete this load?'
                                            )
                                        "
                                    >
                                        <span v-text="$gettext('undo')" />
                                    </a>
                                    <a
                                        v-if="
                                            event.status == 'unloaded' ||
                                                event.status == 'failed' ||
                                                event.status == 'cancelled'
                                        "
                                        @click="
                                            emitCleanLoadEvent(event.loadid)
                                        "
                                    >
                                        <span
                                            v-text="
                                                $gettext('remove from history')
                                            "
                                        />
                                    </a>
                                    <a
                                        v-if="event.status == 'running'"
                                        @click="emitStopEtl(event.loadid)"
                                    >
                                        <span v-text="$gettext('stop')" />
                                    </a>
                                </div>
                                <div class="status">
                                    <button
                                        v-if="event.status == 'completed'"
                                        class="btn btn-warning"
                                        style="width: 150px"
                                    >
                                        <span v-text="$gettext('Indexing')" />
                                    </button>
                                    <button
                                        v-if="event.status == 'validated'"
                                        class="btn btn-warning"
                                        style="width: 150px"
                                    >
                                        <span v-text="$gettext('Running')" />
                                    </button>
                                    <button
                                        v-if="event.status == 'indexed'"
                                        class="btn btn-success"
                                        style="width: 150px"
                                    >
                                        <span v-text="$gettext('Completed')" />
                                    </button>
                                    <button
                                        v-if="event.status == 'unindexed'"
                                        class="btn btn-success"
                                        style="width: 150px"
                                    >
                                        <span
                                            v-text="
                                                $gettext('loaded but unindexed')
                                            "
                                        />
                                    </button>
                                    <button
                                        v-if="event.status == 'failed'"
                                        class="btn btn-danger"
                                        style="width: 150px"
                                    >
                                        <span v-text="$gettext('failed')" />
                                    </button>
                                    <button
                                        v-if="event.status == 'running'"
                                        class="btn btn-warning"
                                        style="width: 150px"
                                    >
                                        <span v-text="$gettext('validating')" />
                                    </button>
                                    <button
                                        v-if="event.status == 'reversing'"
                                        class="btn btn-warning"
                                        style="width: 150px"
                                    >
                                        <span v-text="$gettext('unloading')" />
                                    </button>
                                    <button
                                        v-if="event.status == 'unloaded'"
                                        class="btn btn-sucess"
                                        style="width: 150px"
                                    >
                                        <span v-text="$gettext('unloaded')" />
                                    </button>
                                    <button
                                        v-if="event.status == 'cancelled'"
                                        class="btn btn-sucess"
                                        style="width: 150px"
                                    >
                                        <span v-text="$gettext('cancelled')" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                    <Paginator
                        v-if="loadEvents"
                        :rows="10"
                        :total-records="loadEvents.length"
                        :rows-per-page-options="[10, 20, 30]"
                    />
                </SplitterPanel>
                <SplitterPanel
                    class="flex align-items-center justify-content-center"
                >
                    Load Event Details will go here
                </SplitterPanel>
            </Splitter>
        </div>
    </div>
</template>

<style>
.task-list-search-box {
    display: flex;
    flex-direction: row;
    justify-content: center;
}
.job-list {
    height: 85vh;
}
.task-list {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-content: center;
}
</style>
