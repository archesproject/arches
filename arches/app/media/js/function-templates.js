import { loadComponentDependencies } from "utils/load-component-dependencies";

function removeTrailingCommaFromObject(string) {
    return string.replace(/,\s*}*$/, "}");
}

let functionTemplates;
try {        
    const functionTemplateDataHTML = document.querySelector('#functionTemplateData');
    const functionTemplateData = functionTemplateDataHTML.getAttribute('functionTemplates');
    functionTemplates = JSON.parse(removeTrailingCommaFromObject(functionTemplateData));

    loadComponentDependencies(
        Object.values(functionTemplates).reduce((acc, value) => {
            if (value['component']) {
                acc.push(value['component']);
            }
            return acc;
        }, [])
    );
} catch (error) {
    console.error(error);
}

export default functionTemplates;