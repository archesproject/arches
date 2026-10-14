import ko from 'knockout';


// attaches our Tiptap rich text editor to an element
ko.bindingHandlers.tiptap = {
    init: (element, valueAccessor) => {
        valueAccessor().mount(element);
    },
};
ko.bindingHandlers.tiptap.init = ko.bindingHandlers.tiptap.init.bind(ko.bindingHandlers.tiptap);

export default ko.bindingHandlers.tiptap;
