<script setup>
import Menubar from 'primevue/menubar';
import InputText from 'primevue/inputtext';
import { ref, watch } from 'vue'
import ThemingButtons from '@/ThemingButtons.vue';
import MyActivities from '@/MyActivities.vue';

const items = ref([
    {
        label: 'File',
        icon: 'pi pi-fw pi-file',
        items: [
            {
                label: 'New',
                icon: 'pi pi-fw pi-plus',
                items: [
                    {
                        label: 'Bookmark',
                        icon: 'pi pi-fw pi-bookmark'
                    },
                    {
                        label: 'Video',
                        icon: 'pi pi-fw pi-video'
                    }
                ]
            },
            {
                label: 'Delete',
                icon: 'pi pi-fw pi-trash'
            },
            {
                separator: true
            },
            {
                label: 'Export',
                icon: 'pi pi-fw pi-external-link'
            }
        ]
    },
    {
        label: 'Edit',
        icon: 'pi pi-fw pi-pencil',
        items: [
            {
                label: 'Left',
                icon: 'pi pi-fw pi-align-left'
            },
            {
                label: 'Right',
                icon: 'pi pi-fw pi-align-right'
            },
            {
                label: 'Center',
                icon: 'pi pi-fw pi-align-center'
            },
            {
                label: 'Justify',
                icon: 'pi pi-fw pi-align-justify'
            }
        ]
    },
    {
        label: 'Users',
        icon: 'pi pi-fw pi-user',
        items: [
            {
                label: 'New',
                icon: 'pi pi-fw pi-user-plus'
            },
            {
                label: 'Delete',
                icon: 'pi pi-fw pi-user-minus'
            },
            {
                label: 'Search',
                icon: 'pi pi-fw pi-users',
                items: [
                    {
                        label: 'Filter',
                        icon: 'pi pi-fw pi-filter',
                        items: [
                            {
                                label: 'Print',
                                icon: 'pi pi-fw pi-print'
                            }
                        ]
                    },
                    {
                        icon: 'pi pi-fw pi-bars',
                        label: 'List'
                    }
                ]
            }
        ]
    },
    {
        label: 'Events',
        icon: 'pi pi-fw pi-calendar',
        items: [
            {
                label: 'Edit',
                icon: 'pi pi-fw pi-pencil',
                items: [
                    {
                        label: 'Save',
                        icon: 'pi pi-fw pi-calendar-plus'
                    },
                    {
                        label: 'Delete',
                        icon: 'pi pi-fw pi-calendar-minus'
                    }
                ]
            },
            {
                label: 'Archieve',
                icon: 'pi pi-fw pi-calendar-times',
                items: [
                    {
                        label: 'Remove',
                        icon: 'pi pi-fw pi-calendar-minus'
                    }
                ]
            }
        ]
    },
    {
        label: 'Quit',
        icon: 'pi pi-fw pi-power-off'
    }
]);
</script>

<template>
    <ThemingButtons />
    <div class="dashboard-container">
        <div class="sidebar-container">
            sidebar
        </div>
        <div class="dashboard-content">
            <Menubar :model="items">
                <template #start>
                    <InputText placeholder="Search..." type="text" />
                </template>

                <template #item="{ label, item, props, root, hasSubmenu }">
                    <router-link v-if="item.route" v-slot="routerProps" :to="item.route" custom>
                        <a :href="routerProps.href" v-bind="props.action">
                            <span v-bind="props.icon" />
                            <span v-bind="props.label">{{ label }}</span>
                        </a>
                    </router-link>
                    <a v-else :href="item.url" :target="item.target" v-bind="props.action">
                        <span v-bind="props.icon" />
                        <span v-bind="props.label">{{ label }}</span>
                        <span :class="[hasSubmenu && (root ? 'pi pi-fw pi-angle-down' : 'pi pi-fw pi-angle-right')]" v-bind="props.submenuicon" />
                    </a>
                </template>

                <template #end>
                    <img alt="logo" src="https://primefaces.org/cdn/primevue/images/logo.svg" height="40" class="mr-2" />
                </template>
            </Menubar>
            <MyActivities />
        </div>
    </div>
</template>

<style>
    body {
        margin: 0px;
    }

</style>

<style scoped>
    .dashboard-container {
        display: flex;
    }

    .sidebar-container {
        width: 70px;
        height: 100vh;
        background: #343a40;
        color: #f2f2f2;
        -webkit-transition: width 0.75s ease-in-out;
        transition: width 0.75s ease-in-out;
    }

    .dashboard-content {
        width: 100%;
    }

    :deep(.p-menubar) {
        align-items: flex-start;
    }

    :deep(.p-menubar .p-menubar-end) {
        align-self: flex-start;
    }

    :deep(.p-menubar-end) {
        margin: 0px 0px 0px 10px;
    }

    :deep(.p-menubar-root-list) {
        width: 100%;
        justify-content: flex-end;
    }

    :deep(.p-menuitem-content .p-menuitem-link .p-menuitem-text) {
        color: #999;
        font-size: 14px;
    }

    :deep(.p-menubar-start input) {
        width: 350px;
        height: 36px;
        font-size: 14px;
        margin-top: 4px;
    }

    :deep(.p-menubar-start input::placeholder) {
        color: #999;
    }
</style>
