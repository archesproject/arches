<script setup lang="ts">
import Drawer from "primevue/drawer";

import { useGettext } from "vue3-gettext";

const { $gettext } = useGettext();

const { shouldShowHelpDrawer } = defineProps<{
    shouldShowHelpDrawer: boolean;
}>();

const emit = defineEmits<{
    (event: "update:shouldShowHelpDrawer", value: boolean): void;
}>();

type EdtfExample = {
    primaryValue: string;
    pattern?: string;
    description: string;
    secondaryValue?: string;
};

const edtfExamples: EdtfExample[] = [
    {
        primaryValue: "2021-04-12",
        pattern: $gettext('[year]["-"][month]["-"][day]'),
        description: $gettext(
            "Refers to the calendar date 2021 April 12th with day precision",
        ),
    },
    {
        primaryValue: "2021-04",
        pattern: $gettext('[year]["-"][month]'),
        description: $gettext(
            "Refers to the calendar month April 2021 with month precision",
        ),
    },
    {
        primaryValue: "2021",
        pattern: $gettext("[year]"),
        description: $gettext("Refers to the year 2021 with year precision"),
    },
    {
        primaryValue: "1964/2008",
        description: $gettext(
            "A time interval with calendar year precision, beginning sometime in 1964 and ending sometime in 2008",
        ),
    },
    {
        primaryValue: "2004-06/2006-08",
        description: $gettext(
            "A time interval with calendar month precision, beginning sometime in June 2004 and ending sometime in August of 2006",
        ),
    },
    {
        primaryValue: "2004-02-01/2005",
        description: $gettext(
            "A time interval with calendar year precision, beginning sometime in 2004 and ending sometime in 2005",
        ),
    },
    {
        primaryValue: "Y-100000",
        description: $gettext(
            'The year -100000. "Y" may be used at the beginning of the date string to signify that the date is a year, when (and only when) the year exceeds four digits, i.e. for years later than 9999 or earlier than -9999.',
        ),
    },
    {
        primaryValue: "2001-21",
        description: $gettext(
            'Spring, 2001. The values 21, 22, 23, 24 may be used used to signify "Spring", "Summer", "Autumn", "Winter", respectively, in place of a month value (01 through 12) for a year-and-month format string',
        ),
    },
    {
        primaryValue: "1984?",
        description: $gettext(
            "Year uncertain (possibly the year 1984, but not definitely)",
        ),
    },
    {
        primaryValue: "2004-06~",
        secondaryValue: "2004-06-11%",
        description: $gettext(
            "Entire date (year-month-day) uncertain and approximate",
        ),
    },
];

function handleUpdateVisible(nextVisible: boolean) {
    emit("update:shouldShowHelpDrawer", nextVisible);
}
</script>

<template>
    <Drawer
        :visible="shouldShowHelpDrawer"
        position="right"
        style="height: 100%; width: 30%"
        :modal="true"
        :dismissable="true"
        @update:visible="handleUpdateVisible"
    >
        <h4>{{ $gettext("Extended Date/Time Formats (EDTF)") }}</h4>

        <p>
            {{
                $gettext(
                    "The EDTF datatype allows you to describe dates (even uncertain dates). You can find a summary of the standard here: EDTF Date Specfication (Library of Congress)",
                )
            }}
        </p>

        <p>{{ $gettext("Some common encodings:") }}</p>

        <section
            v-for="currentEdtfExample in edtfExamples"
            :key="currentEdtfExample.primaryValue"
            class="edtf-example"
        >
            <p class="edtf-example-values">
                <b class="edtf-example-value">
                    {{ currentEdtfExample.primaryValue }}
                </b>

                <b
                    v-if="currentEdtfExample.secondaryValue"
                    class="edtf-example-value"
                >
                    {{ currentEdtfExample.secondaryValue }}
                </b>
            </p>

            <p
                v-if="currentEdtfExample.pattern"
                class="edtf-example-pattern"
            >
                {{ currentEdtfExample.pattern }}
            </p>

            <p class="edtf-example-description">
                {{ currentEdtfExample.description }}
            </p>
        </section>
    </Drawer>
</template>

<style scoped>
p {
    margin-bottom: 0.5rem;
}

.edtf-example {
    margin-bottom: 0.75rem;
}

.edtf-example-values {
    display: flex;
    gap: 0.5rem;
}

.edtf-example-pattern {
    font-family: monospace;
}

.edtf-example-description {
    margin-top: 0.15rem;
}
</style>
