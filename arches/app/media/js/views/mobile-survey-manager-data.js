define([], function() {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const mobileSurveyManagerDataHTML = document.querySelector('#mobileSurveyManagerData');
    const mobileSurveyManagerData = mobileSurveyManagerDataHTML.getAttribute('mobileSurveyManagerData');

    const parsedMobileSurveyManagerData = JSON.parse(removeTrailingCommaFromObject(mobileSurveyManagerData));

    return parsedMobileSurveyManagerData;
});