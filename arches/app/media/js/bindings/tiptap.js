import ko from 'knockout';


// Points Tiptap rich text editor to a DOM element to draw editing area into
ko.bindingHandlers.tiptap = {
    init: (element, valueAccessor) => {
        valueAccessor().mount(element);
    },
};

export default ko.bindingHandlers.tiptap;
