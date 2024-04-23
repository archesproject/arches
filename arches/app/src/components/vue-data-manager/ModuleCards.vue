<script setup>
import { useGettext } from "vue3-gettext";

const props = defineProps(["filteredModules"]);
const emit = defineEmits(["selectModule"]);

const emitSelectModule = (etlModule) => {
    emit("selectModule", etlModule);
};
</script>
<template>
    <div class="vue-manager-card-container">
        <template v-for="etlModule in filteredModules">
            <div
                class="vue-manager-card"
                :style="{ backgroundColor: etlModule.config.bgColor }"
                @click="emitSelectModule(etlModule)"
            >
                <div class="vue-manager-card-title">
                    {{ etlModule.name }}
                </div>
                <div
                    class="vue-manager-workflow-select-wf-circle"
                    :style="{
                        backgroundColor: etlModule.config.circleColor,
                    }"
                >
                    <div
                        class="vue-manager-card-icon"
                        :class="etlModule.icon"
                    ></div>
                </div>
                <div class="vue-manager-card-subtitle">
                    {{ etlModule.description }}
                </div>
            </div>
        </template>
    </div>
</template>
<style>
.vue-manager-card {
    width: 200px;
    height: 200px;
    margin: 10px;
    border-radius: 7px;
    display: flex;
    justify-content: space-evenly;
    flex-direction: column;
    align-items: center;
    padding: 10px;
    box-shadow: 3px 3px 2px 0px lightgrey;
    cursor: pointer;
}

.vue-manager-card-container {
    display: flex;
    flex-wrap: wrap;
}

.vue-manager-workflow-select-wf-circle {
    width: 70px;
    height: 70px;
    display: inline-block;
    text-align: center;
    padding: 18px 12px;
    border-radius: 40px;
    border: 1px solid #747474;
}

.vue-manager-card-icon {
    color: white;
    font-size: 2.8rem;
    padding-top: 0px;
}

.vue-manager-card-title {
    font-size: medium;
    color: white;
    text-align: center;
    font-weight: 600;
}

.vue-manager-card-subtitle {
    color: white;
    font-size: small;
    text-align: center;
}
</style>
