function removeTrailingCommaFromObject(string) {
    return string.replace(/,\s*}*$/, "}");
}

let parsedProfileManagerData;

try {
    const profileManagerDataHTML = document.querySelector('#profileManagerData');
    const profileManagerData = profileManagerDataHTML.getAttribute('profileManagerData');
    parsedProfileManagerData = JSON.parse(removeTrailingCommaFromObject(profileManagerData));
} catch (error) {
    console.error(error);
}

export default parsedProfileManagerData;