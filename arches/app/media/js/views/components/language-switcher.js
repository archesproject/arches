define(['knockout', 'templates/views/components/language-switcher.htm', 'js-cookie', 'bindings/select2-query'], function(ko, languageSwitcherTemplate, Cookies) {
    /**
    * knockout components namespace used in arches
    * @external "ko.components"
    * @see http://knockoutjs.com/documentation/component-binding.html
    */

    /**
    * registers a language-switcher component for use in forms
    * @function external:"ko.components".language-switcher
    * @param {object} params
    * @param {string} params.current_language - the currently active language in the application
    */
    return ko.components.register('views/components/language-switcher', {
        viewModel: function(params) {
            this.formid = Math.random();
            this.value = ko.observable(params.current_language);
            this.csrfToken = Cookies.get('csrftoken');
            this.value.subscribe(function(val){
                if (val) {
                    document.getElementById(this.formid).submit();
                }
            }, this);
        },
        template: languageSwitcherTemplate,
    });
});