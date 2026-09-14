import { defineStore } from "pinia";
import { ref } from "vue";

import { fetchLanguages } from "@/arches_vue_components/widgets/api.ts";

import type { Language } from "@/arches_vue_components/types.ts";

export const useLanguageStore = defineStore(
    "arches_vue_components:language",
    () => {
        const languages = ref<Language[]>([]);
        let fetchPromise: Promise<Language[]> | null = null;

        function fetchAllLanguages(): Promise<Language[]> {
            if (!fetchPromise) {
                fetchPromise = fetchLanguages()
                    .then((response: { languages: Language[] }) => {
                        languages.value = response.languages;
                        return response.languages;
                    })
                    .catch((error: unknown) => {
                        fetchPromise = null;
                        throw error;
                    });
            }
            return fetchPromise;
        }

        return { languages, fetchAllLanguages };
    },
);
