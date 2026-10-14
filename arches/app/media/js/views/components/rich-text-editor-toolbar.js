import ko from 'knockout';
import arches from 'arches';
import richTextEditorToolbarTemplate from 'templates/views/components/rich-text-editor-toolbar.htm';


const writeToClipboard = async (editor, isCut) => {
    const { state, view } = editor;
    if (state.selection.empty) {
        return;
    }
    const { dom, text } = view.serializeForClipboard(state.selection.content());
    await navigator.clipboard.write([new ClipboardItem({
        'text/html': new Blob([dom.innerHTML], { type: 'text/html' }),
        'text/plain': new Blob([text], { type: 'text/plain' }),
    })]);
    if (isCut) {
        editor.chain().focus().deleteSelection().run();
    }
};

// browsers block pasting from a button with execCommand, so read the clipboard and paste it the same way as Ctrl+V
const pasteFromClipboard = async (editor, asPlainText) => {
    if (asPlainText) {
        editor.view.pasteText(await navigator.clipboard.readText());
        return;
    }
    const [item] = await navigator.clipboard.read();
    if (item?.types.includes('text/html')) {
        editor.view.pasteHTML(await (await item.getType('text/html')).text());
    } else if (item?.types.includes('text/plain')) {
        editor.view.pasteText(await (await item.getType('text/plain')).text());
    }
};

const setLink = (editor) => {
    const href = window.prompt(arches.translations.linkUrl, editor.getAttributes('link').href ?? '');
    if (href === null) {
        return;
    }
    const chain = editor.chain().focus().extendMarkRange('link');
    (href ? chain.setLink({ href }) : chain.unsetLink()).run();
};

const insertImage = (editor) => {
    const src = window.prompt(arches.translations.imageUrl);
    if (src) {
        const alt = window.prompt(arches.translations.imageDescription) ?? '';
        editor.chain().focus().setImage({ src, alt }).run();
    }
};

// Defines each option within the toolbar.
// - command(chain) - adds Tiptap commands to a chain
// - action(editor) - additional, bespoke functions 
const toolbarItems = {
    cut: { action: editor => writeToClipboard(editor, true), isDisabled: editor => editor.state.selection.empty },
    copy: { action: editor => writeToClipboard(editor, false), isDisabled: editor => editor.state.selection.empty },
    paste: { action: editor => pasteFromClipboard(editor, false) },
    pasteText: { action: editor => pasteFromClipboard(editor, true) },
    undo: { command: chain => chain.undo() },
    redo: { command: chain => chain.redo() },
    link: { action: setLink, isActive: editor => editor.isActive('link') },
    unlink: { command: chain => chain.extendMarkRange('link').unsetLink(), isDisabled: editor => !editor.isActive('link') },
    image: { action: insertImage },
    insertTable: { command: chain => chain.insertTable({ rows: 3, cols: 3, withHeaderRow: false }) },
    addRowBefore: { command: chain => chain.addRowBefore() },
    addRowAfter: { command: chain => chain.addRowAfter() },
    deleteRow: { command: chain => chain.deleteRow() },
    addColumnBefore: { command: chain => chain.addColumnBefore() },
    addColumnAfter: { command: chain => chain.addColumnAfter() },
    deleteColumn: { command: chain => chain.deleteColumn() },
    toggleHeaderRow: { command: chain => chain.toggleHeaderRow() },
    deleteTable: { command: chain => chain.deleteTable() },
    horizontalRule: { command: chain => chain.setHorizontalRule() },
    bold: { command: chain => chain.toggleBold(), isActive: editor => editor.isActive('bold') },
    italic: { command: chain => chain.toggleItalic(), isActive: editor => editor.isActive('italic') },
    underline: { command: chain => chain.toggleUnderline(), isActive: editor => editor.isActive('underline') },
    strike: { command: chain => chain.toggleStrike(), isActive: editor => editor.isActive('strike') },
    removeFormat: { command: chain => chain.unsetAllMarks().clearNodes() },
    orderedList: { command: chain => chain.toggleOrderedList(), isActive: editor => editor.isActive('orderedList') },
    bulletList: { command: chain => chain.toggleBulletList(), isActive: editor => editor.isActive('bulletList') },
    outdent: { command: chain => chain.liftListItem('listItem') },
    indent: { command: chain => chain.sinkListItem('listItem') },
    blockquote: { command: chain => chain.toggleBlockquote(), isActive: editor => editor.isActive('blockquote') },
    paragraph: { command: chain => chain.setParagraph(), isActive: editor => editor.isActive('paragraph') },
    heading1: { command: chain => chain.setHeading({ level: 1 }), isActive: editor => editor.isActive('heading', { level: 1 }), },
    heading2: { command: chain => chain.setHeading({ level: 2 }), isActive: editor => editor.isActive('heading', { level: 2 }), },
    heading3: { command: chain => chain.setHeading({ level: 3 }), isActive: editor => editor.isActive('heading', { level: 3 }), },
    heading4: { command: chain => chain.setHeading({ level: 4 }), isActive: editor => editor.isActive('heading', { level: 4 }), },
    heading5: { command: chain => chain.setHeading({ level: 5 }), isActive: editor => editor.isActive('heading', { level: 5 }), },
    heading6: { command: chain => chain.setHeading({ level: 6 }), isActive: editor => editor.isActive('heading', { level: 6 }), },
    codeBlock: { command: chain => chain.setCodeBlock(), isActive: editor => editor.isActive('codeBlock') },
};

const textFormats = ['paragraph', 'heading1', 'heading2', 'heading3', 'heading4', 'heading5', 'heading6', 'codeBlock'];

/**
* The Tiptap rich text editor toolbar.
* @param {object} params
* @param {Editor} params.editor - the Tiptap editor
* @param {ko.observable<boolean>} params.disabled - when true, the toolbar is inert: it can't be clicked or focused
* @param {HTMLElement} element - the component's element
*/
const RichTextEditorToolbar = function(params, element) {
    const editor = params.editor;

    this.disabled = params.disabled;
    this.isTableMenuOpen = ko.observable(false);

    // get isDisabled and isActive for each item name
    const getState = () => Object.fromEntries(Object.entries(toolbarItems).map(([name, item]) => [name, {
        isDisabled: item.isDisabled?.(editor) ?? false,
        isActive: item.isActive?.(editor) ?? false,
    }]));

    // updated after every change to the editor's content or selection
    this.state = ko.observable(getState());
    const onTransaction = () => this.state(getState());
    editor.on('transaction', onTransaction);

    this.format = ko.pureComputed(() => textFormats.find(name => this.state()[name].isActive) ?? '');
    console.log(this.format);

    this.run = name => () => {
        const item = toolbarItems[name];
        console.log(item, name);
        this.isTableMenuOpen(false);
        if (item.action) {
            item.action(editor);
        } else {
            item.command(editor.chain().focus()).run();
        }
    };

    this.onTextFormatChange = (_data, event) => {
        this.run(event.target.value)();
    };

    // roving tabindex: only the most recently focused control is in the tab order
    const getControls = () => Array.from(element.querySelectorAll('.rich-text-editor-toolbar-button, .rich-text-editor-toolbar-select'));

    const setCurrentControl = (control) => {
        getControls().forEach((c) => { c.tabIndex = c === control ? 0 : -1; });
    };

    this.onFocusIn = (_data, event) => {
        if (getControls().includes(event.target)) {
            setCurrentControl(event.target);
        }
        return true;
    };

    this.onKeydown = (_data, event) => {
        const controls = getControls();
        const index = controls.indexOf(document.activeElement);
        const moveTo = index === -1 ? undefined : {
            ArrowRight: (index + 1) % controls.length,
            ArrowLeft: (index - 1 + controls.length) % controls.length,
            Home: 0,
            End: controls.length - 1,
        }[event.key];
        if (moveTo !== undefined) {
            controls[moveTo].focus();
        } else if (event.key === 'Escape' && this.isTableMenuOpen()) {
            this.isTableMenuOpen(false);
            element.querySelector('.rich-text-editor-toolbar-menu > button').focus();
        } else if (event.key === 'Escape') {
            editor.commands.focus();
        } else {
            return true;
        }
    };

    // the table menu is a disclosure: a button showing a list of buttons, closed when focus or a click leaves it
    this.toggleTableMenu = () => {
        this.isTableMenuOpen(!this.isTableMenuOpen());
    };

    const closeTableMenuIfOutside = (event) => {
        if (!element.querySelector('.rich-text-editor-toolbar-menu')?.contains(event.target)) {
            this.isTableMenuOpen(false);
        }
    };
    document.addEventListener('focusin', closeTableMenuIfOutside);
    document.addEventListener('pointerdown', closeTableMenuIfOutside);

    this.koDescendantsComplete = () => {
        setCurrentControl(getControls()[0]);
    };

    this.dispose = () => {
        editor.off('transaction', onTransaction);
        document.removeEventListener('focusin', closeTableMenuIfOutside);
        document.removeEventListener('pointerdown', closeTableMenuIfOutside);
    };
};

export default ko.components.register('views/components/rich-text-editor-toolbar', {
    viewModel: {
        createViewModel: (params, componentInfo) => new RichTextEditorToolbar(params, componentInfo.element),
    },
    template: richTextEditorToolbarTemplate,
});
