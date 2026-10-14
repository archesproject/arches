import ko from 'knockout';
import arches from 'arches';
import createRichTextEditor from 'utils/rich-text-editor';
import 'views/components/rich-text-editor-toolbar';


// A binding for the Arches Tiptap rich text editor and toolbar. 
ko.bindingHandlers.tiptap = {
    init: function(element, valueAccessor, allBindings, _viewModel, bindingContext) {
        const modelValue = valueAccessor();
        const direction = allBindings.get('direction') || arches.activeLanguageDir;
        const disabled = allBindings.get('attr')?.disabled;
        const placeholder = ko.unwrap(allBindings.get('placeholder'));
        const isDisabled = ko.observable(!!ko.unwrap(disabled));

        const toolbarElement = document.createElement('div'); 
        const subscriptions = [];

        const { editor, setContent } = createRichTextEditor(element, {
            content: ko.unwrap(modelValue) || (allBindings.get('isConfigForm') ? placeholder : ''),
            editable: !isDisabled(),
            direction: ko.unwrap(direction),
            placeholder: placeholder,
            onChange: (newValue) => {
                if (ko.isWriteableObservable(modelValue) && newValue !== (modelValue() || '')) {
                    modelValue(newValue);
                }
            },
            onFocusToolbar: () => toolbarElement.querySelector('[tabindex="0"]')?.focus(),
        });

        element.prepend(toolbarElement);
        ko.applyBindingsToNode(toolbarElement, {
            component: {
                name: 'views/components/rich-text-editor-toolbar',
                params: { editor, disabled: isDisabled },
            },
        }, bindingContext);

        if (ko.isSubscribable(modelValue)) {
            subscriptions.push(modelValue.subscribe(newValue => setContent(newValue)));
        }
        if (ko.isSubscribable(direction)) {
            subscriptions.push(direction.subscribe((newValue) => { editor.view.dom.dir = newValue; }));
        }
        if (ko.isSubscribable(disabled)) {
            subscriptions.push(disabled.subscribe(newValue => isDisabled(!!newValue)));
        }
        subscriptions.push(isDisabled.subscribe(newValue => editor.setEditable(!newValue, false)));

    }
};
ko.bindingHandlers.tiptap.init = ko.bindingHandlers.tiptap.init.bind(ko.bindingHandlers.tiptap);

export default ko.bindingHandlers.tiptap;
