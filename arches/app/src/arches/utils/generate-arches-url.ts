export default function (
    urlName: string,
    languageCode: string | null = null,
    urlParams = {},
) {
    // @ts-expect-error  ARCHES_URLS is defined globally
    let url = ARCHES_URLS[urlName];

    if (!url) {
        throw new Error(`Key '${urlName}' not found in JSON object`);
    }

    if (url.includes("{language_code}")) {
        if (!languageCode) {
            const htmlLang = document.documentElement.lang;
            languageCode = htmlLang.split("-")[0];
        }

        url = url.replace("{language_code}", languageCode);
    }

    Object.entries(urlParams).forEach(([key, value]) => {
        url = url.replace(new RegExp(`{${key}}`, "g"), value);
    });

    return url;
}
