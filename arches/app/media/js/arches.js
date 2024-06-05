define(['utils/set-csrf-token'], function() {
    function removeTrailingCommaFromArray(string) {
        return string.replace(/, *]*$/, "]");
    }
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }
    function convertToCamelCase(string) {
        return string.replace(/-([a-z])/g, function(g) { return g[1].toUpperCase(); });
    }

    const archesUrlHTMLObjects = document.querySelectorAll('.arches-urls');
    const parsedArchesUrls = {};
    for (let archesUrlHTMLObject of archesUrlHTMLObjects) {
        for (let attribute of archesUrlHTMLObject.attributes) {
            if (
                attribute.specified
                && attribute.name !== 'style'
                && attribute.name !== 'class'
            ) {
                try {
                    let functionFromString = Function("return" + attribute.value);
                    let result = functionFromString();

                    if (!result) {
                        result = "";
                    }
                    if (typeof result === 'object') {
                        result = String(result);
                    }
                    parsedArchesUrls[attribute.name] = result;
                } catch (error) {
                    parsedArchesUrls[attribute.name] = String(attribute.value);
                }
            }
        }
    }

    const archesTranslationsHTMLObjects = document.querySelectorAll('.arches-translations');
    const parsedArchesTranslations = {};
    for (let archesTranslationsHTMLObject of archesTranslationsHTMLObjects) {
        for (let attribute of archesTranslationsHTMLObject.attributes) {
            if (
                attribute.specified
                && attribute.name !== 'style'
                && attribute.name !== 'class'
            ) {
                try {
                    let functionFromString = Function("return" + attribute.value);
                    let result = functionFromString();

                    if (!result) {
                        result = "";
                    }

                    parsedArchesTranslations[convertToCamelCase(attribute.name)] = result;
                } catch (error) {
                    parsedArchesTranslations[convertToCamelCase(attribute.name)] = JSON.parse(attribute.value);
                }
            }
        }
    }

    const archesDataHTMLObjects = document.querySelectorAll('.arches-data');
    const parsedArchesData = {};
    for (let archesDataHTMLObject of archesDataHTMLObjects) {
        for (let attribute of archesDataHTMLObject.attributes) {
            if (
                attribute.specified
                && attribute.name !== 'style'
                && attribute.name !== 'class'
            ) {
                const camelCaseName = convertToCamelCase(attribute.name);
    
                try {  // first try parsing value
                    parsedArchesData[camelCaseName] = JSON.parse(attribute.value);
                } catch (e) {
                    try {  // if it fails, try removing trailing comma from object
                        parsedArchesData[camelCaseName] = JSON.parse(removeTrailingCommaFromObject(attribute.value));
                    } catch (e) {  // if it fails, try removing trailing comma from array
                        try {
                            parsedArchesData[camelCaseName] = JSON.parse(removeTrailingCommaFromArray(attribute.value));
                        } catch (e) {  // if it fails, coerce value to string
                            parsedArchesData[camelCaseName] = JSON.parse(`"${attribute.value}"`);
                        }
                    }
                }
            }
        }
    }

    const archesObject = { ...parsedArchesData };

    if (Object.keys(parsedArchesTranslations).length) {
        archesObject["translations"] = parsedArchesTranslations;
    }

    if (Object.keys(parsedArchesUrls).length) {
        archesObject["urls"] = parsedArchesUrls;
    }

    return archesObject;
});
