define([], function() {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const profileManagerDataHTML = document.querySelector('#profileManagerData');
    const profileManagerData = profileManagerDataHTML.getAttribute('profileManagerData');

    const parsedprofileManagerData = JSON.parse(removeTrailingCommaFromObject(profileManagerData));

    return parsedprofileManagerData;
});