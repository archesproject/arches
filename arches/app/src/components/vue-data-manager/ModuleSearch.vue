<script setup>
import { ref, watch } from "vue";
import InputText from "primevue/inputtext";

const emit = defineEmits(["moduleSearch"]);

const moduleSearchValue = ref();

watch(moduleSearchValue, (val) => {
    emit("moduleSearch", val);
});
</script>

<template>
    <div id="search-box">
        <span class="p-input-icon-left">
            <i class="pi pi-search" />
            <InputText
                v-model="moduleSearchValue"
                :placeholder="$gettext('Filter Modules...')"
            />
        </span>
    </div>
</template>

<style scoped>
.search-box {
    height: 100%;
    margin: 10px;
}
.p-inputtext {
    height: 30px;
    margin: 10px;
    font-size: larger;
}
</style>
