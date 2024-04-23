<script setup>
import { ref, onMounted, watch } from "vue";
import { useGettext } from "vue3-gettext";
import TabView from "primevue/tabview";
import TabPanel from "primevue/tabpanel";
import Button from "primevue/button";
import TaskStatus from "./TaskStatus.vue";
import TileExcelImporter from "./etl_modules/TileExcelImporter.vue";
import BranchExcelImporter from "./etl_modules/BranchExcelImporter.vue";
import ImportSingleCsv from "./etl_modules/import-single-csv/ImportSingleCsv.vue";
import BranchExcelExporter from "./etl_modules/branch-excel-exporter/BranchExcelExporter.vue";
import ModuleSearch from "./ModuleSearch.vue";
import ModuleCards from "./ModuleCards.vue";
import arches from "arches";
import Cookies from "js-cookie";
import AlertViewModel from "../../../media/js/viewmodels/alert";
import loadComponentDependencies from "utils/load-component-dependencies";

const modules = {
    ImportSingleCsv,
    TileExcelImporter,
    BranchExcelImporter,
    BranchExcelExporter,
};

const { $gettext } = useGettext();
const activeTab = ref(0);
const alert = ref();
const etlModules = ref([]);
const filteredModules = ref([]);
const loadEvents = ref();
const loading = ref("true");
const paginator = ref();
const search = ref("");
const selectedLoadEvent = ref();
const selectedModule = ref();
const selectedModuleType = ref("import");
const validated = ref();
const validationErrors = ref();

const ModuleTypeButtons = [
    { label: $gettext("Import"), value: "import" },
    { label: $gettext("Edit"), value: "edit" },
    { label: $gettext("Export"), value: "export" },
];

watch(activeTab, (val) => {
    if (val == 2) {
        loadEvents.value = null;
        selectedLoadEvent.value = null;
        setTimeout(function () {
            fetchLoadEvent(1);
        }, 300);
    }
    if (val == 0) {
        selectedModule.value = null;
    }
});

watch(loadEvents, (loadEvents) => {
    if (loadEvents) {
        const loadEventIds = loadEvents.map((loadEvent) => loadEvent.loadid);
        if (!loadEventIds.includes(selectedLoadEvent.value?.loadid)) {
            selectedLoadEvent.value = loadEvents[0];
        }
    }
});

watch(search, () => {
    if (search.value.length > 0) {
        filteredModules.value = etlModules.value.filter((module) =>
            module.name.toLowerCase().includes(search.value.toLowerCase())
        );
    } else {
        selectModuleType(selectedModuleType.value);
    }
});

watch(selectedLoadEvent, (val) => {
    if (val) {
        selectedModule.value = val.etl_module;
        fetchValidation(val.loadid);
    } else {
        if (loadEvents.value && loadEvents.value.length) {
            selectedLoadEvent.value = loadEvents.value[0];
        }
    }
});

async function prefetch() {
    const url = arches.urls.etl_manager + "?action=modules";
    window
        .fetch(url)
        .then(function (response) {
            if (response.ok) {
                return response.json();
            }
        })
        .then(function (data) {
            etlModules.value = data.map(function (etl) {
                loadComponentDependencies([`${etl.component}`]);
                return etl;
            });
            loading.value = false;
            filteredModules.value = etlModules.value.filter(function (module) {
                return module.etl_type === "import";
            });
        });
    activeTab.value = 0;
}

const cleanLoadEvent = (loadid) => {
    const url = `${arches.urls.etl_manager}?action=cleanEvent&loadid=${loadid}`;
    window
        .fetch(url)
        .then(function (response) {
            if (response.ok) {
                return response.json();
            }
        })
        .then(function (data) {
            console.log(data);
            prefetch();
            activeTab.value = 2;
        });
};

const fetchLoadEvent = (page) => {
    if (activeTab.value === 2) {
        if (!page) {
            page = paginator.vlaue?.current_page
                ? paginator.value.current_page
                : 1;
        }
        const url = arches.urls.etl_manager + "?action=loadEvent&page=" + page;
        window
            .fetch(url)
            .then(function (response) {
                if (response.ok) {
                    return response.json();
                }
            })
            .then(function (data) {
                data.events.map((event) => {
                    event.loading = ref(false);
                });
                loadEvents.value = data.events;
                paginator.value = data.paginator;
                const newSelectedEventData = data.events.find(
                    (item) => item.loadid === selectedLoadEvent.value?.loadid
                );
                if (
                    newSelectedEventData &&
                    newSelectedEventData.status !=
                        selectedLoadEvent.value.status
                ) {
                    selectedLoadEvent.value = newSelectedEventData;
                }
            });
    }
};

const fetchValidation = (loadid) => {
    const url = arches.urls.etl_manager + "?action=validate&loadid=" + loadid;
    window
        .fetch(url)
        .then(function (response) {
            if (response.ok) {
                return response.json();
            }
        })
        .then(function (data) {
            validated.value = true;
            const errors = data.data;
            errors.map((error) => {
                error.showDetails = ko.observable(false);
                error.details = ko.observable();
                error.nodeAlias = self
                    .selectedLoadEvent()
                    ?.load_details?.mapping?.find(
                        (x) => x.field.trim() == error.source.trim()
                    )?.node;
            });
            validationErrors.value = errors;
        });
};

const reverseTransactions = (event, undoAlertTitle, undoAlertMessage) => {
    const formData = new FormData();
    const url = arches.urls.etl_manager;
    event.status = "reversing";
    formData.append("loadid", event.loadid);
    formData.append("module", event.etl_module.etlmoduleid);
    formData.append("action", "reverse");
    window
        .fetch(url, {
            method: "POST",
            body: formData,
            credentials: "include",
            headers: {
                "X-CSRFToken": Cookies.get("csrftoken"),
            },
        })
        .then(function (response) {
            return response.json();
        })
        .then(function () {
            fetchLoadEvent();
        });
};

const moduleSearch = (searchValue) => {
    search.value = searchValue;
};

const selectModule = (etlModule) => {
    selectedModule.value = etlModule;
    activeTab.value = 1;
};

const selectModuleType = (moduleType) => {
    selectedModuleType.value = moduleType;
    filteredModules.value = etlModules.value.filter(function (module) {
        return module.etl_type === moduleType;
    });
};

const stopEtl = (loadid) => {
    const url = arches.urls.etl_manager + "?action=stop&loadid=" + loadid;
    window
        .fetch(url)
        .then(function (response) {
            if (response.ok) {
                return response.json();
            }
        })
        .then(function (data) {
            console.log(data);
        });
};

const updateSelectedLoadEvent = (event) => {
    selectedLoadEvent.value = event;
};

onMounted(async () => {
    await prefetch();
});
setInterval(fetchLoadEvent, 5000);
</script>

<template>
    <TabView v-model:activeIndex="activeTab">
        <TabPanel :header="$gettext('Start')">
            <div class="data-manager-button-container">
                <div class="data-manager-button-container">
                    <Button
                        v-for="ModuleTypeButton in ModuleTypeButtons"
                        :label="ModuleTypeButton['label']"
                        @click="selectModuleType(ModuleTypeButton['value'])"
                    />
                </div>
                <ModuleSearch @moduleSearch="moduleSearch" />
            </div>
            <ModuleCards
                :filteredModules="filteredModules"
                @selectModule="selectModule"
            />
        </TabPanel>
        <TabPanel
            :header="$gettext('Task Details')"
            :disabled="!selectedModule"
        >
            <component
                v-if="selectedModule"
                :is="modules[selectedModule.classname]"
                :etlModuleId="[selectedModule.etlmoduleid]"
            />
        </TabPanel>
        <TabPanel :header="$gettext('Task Status')">
            <TaskStatus
                :loadEvents="loadEvents"
                :selectedLoadEvent="selectedLoadEvent"
                @reverseTransactions="reverseTransactions"
                @cleanLoadEvent="cleanLoadEvent"
                @stopEtl="stopEtl"
                @updateSelectedLoadEvent="updateSelectedLoadEvent"
            />
        </TabPanel>
        <TabPanel :header="$gettext('Templates')" disabled="true">
            <p class="m-0">
                At vero eos et accusamus et iusto odio dignissimos ducimus qui
                blanditiis praesentium voluptatum deleniti atque corrupti quos
                dolores et quas molestias excepturi sint occaecati cupiditate
                non provident, similique sunt in culpa qui officia deserunt
                mollitia animi, id est laborum et dolorum fuga. Et harum quidem
                rerum facilis est et expedita distinctio. Nam libero tempore,
                cum soluta nobis est eligendi optio cumque nihil impedit quo
                minus.
            </p>
        </TabPanel>
    </TabView>
</template>

<style>
.data-manager-button-container {
    width: calc(100vw / 2);
    display: flex;
    flex-direction: row;
    align-items: center;
}

/* .p-component {
    height: 100%;
} */

.p-tabview-panels {
    height: 100%;
    width: 100%;
}

.p-tabview-nav {
    display: flex;
    justify-content: space-between;
    /* width: calc(100vw / 2); */
    width: 100%;
}

.p-tabview-nav-content {
    height: 45px;
}

.p-tabview-header {
    flex-grow: 4;
    font-size: medium;
}

li.p-tabview-header.p-highlight {
    background-color: white;
}

.p-tabview-header-action {
    height: 45px;
    justify-content: center;
    outline: none;
}
.data-manager-button-container {
    width: calc(100vw / 2);
    display: flex;
    flex-direction: row;
    align-items: center;
}

.p-button {
    width: 100px;
    background-color: lightgrey;
    border: lightgrey;
    margin: 5px;
}

.p-button-label {
    font-size: small;
    font-weight: bold;
}
</style>
