define(['jquery', 'knockout', 'arches'], function($, ko, arches) {
    const stringUtils = {
        compareTwoStrings: function(str1, str2) {
            // uses dice coefficient for string similarity score
            if (str1.length < 2 || str2.length < 2) return 0;
            let set1 = new Set();
            let set2 = new Set();
            for (let i = 0; i < str1.length - 1; i++) {
                const bigram = str1.substr(i, 2);
                set1.add(bigram);
            }
            for (let i = 0; i < str2.length - 1; i++) {
                const bigram = str2.substr(i, 2);
                set2.add(bigram);
            }
            const intersection = new Set([...set1].filter(x => set2.has(x)));
            return (2 * intersection.size) / (set1.size + set2.size);
        },
        normalizeText: function(text) { return text.toLowerCase().replace(/\W+/g, ''); },
    };
    return stringUtils;
});
