import ko from 'knockout';
import arches from 'arches';

ko.components.loaders.unshift({
    loadTemplate: function (_name, relativeTemplatePath, callback) {
        fetch(arches.urls.root + relativeTemplatePath).then(response => {
            return response.text();
        }).then(html => {
            const range = document.createRange();
            range.selectNode(document.body);

            const fragment = range.createContextualFragment(html);
            callback(Array.from(fragment.childNodes));
        }).catch(error => {
            console.error('Template load failed:', relativeTemplatePath, error);
        });
    }
});
