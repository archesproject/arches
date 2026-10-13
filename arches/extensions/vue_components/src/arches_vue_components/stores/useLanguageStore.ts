import { defineStore } from "pinia";
import { ref } from "vue";

import { fetchLanguages } from "@/arches_vue_components/widgets/api.ts";

import type { Language } from "@/arches_vue_components/types.ts";

export const useLanguageStore = defineStore(
    "arches_vue_components:language",
    () => {
        const languages = ref<Language[]>([]);
        const requestLanguageCode = ref<string | null>(null);
        let fetchPromise: Promise<Language[]> | null = null;

        function fetchAllLanguages(): Promise<Language[]> {
            if (!fetchPromise) {
                fetchPromise = fetchLanguages()
                    .then(
                        (response: {
                            languages: Language[];
                            request_language: string;
                        }) => {
                            languages.value = response.languages;
                            requestLanguageCode.value =
                                response.request_language;
                            return response.languages;
                        },
                    )
                    .catch((error: unknown) => {
                        fetchPromise = null;
                        throw error;
                    });
            }
            return fetchPromise;
        }

        return { languages, requestLanguageCode, fetchAllLanguages };
    },
);
