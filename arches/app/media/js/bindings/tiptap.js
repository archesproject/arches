import ko from 'knockout';


// Points Tiptap rich text editor to a DOM element to draw editing area into
ko.bindingHandlers.tiptap = {
    init: (element, valueAccessor) => {
        valueAccessor().mount(element);
    },
};
ko.bindingHandlers.tiptap.init = ko.bindingHandlers.tiptap.init.bind(ko.bindingHandlers.tiptap);

export default ko.bindingHandlers.tiptap;
