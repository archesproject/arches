import ko from 'knockout';
import arches from 'arches';
import { Editor } from '@tiptap/core';
import StarterKit from '@tiptap/starter-kit';
import { Image } from '@tiptap/extension-image';
import { Subscript } from '@tiptap/extension-subscript';
import { Superscript } from '@tiptap/extension-superscript';
import { TableKit } from '@tiptap/extension-table';
import { dropdown } from 'bootstrap';
import richTextEditorTemplate from 'templates/views/components/rich-text-editor.htm';
import 'bindings/tiptap';


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
    link: { isActive: editor => editor.isActive('link') },
    image: { isActive: editor => editor.isActive('image') },
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
    subscript: { command: chain => chain.toggleSubscript(), isActive: editor => editor.isActive('subscript') },
    superscript: { command: chain => chain.toggleSuperscript(), isActive: editor => editor.isActive('superscript') },
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

/**
* registers a rich-text-editor component: a Tiptap editor with a toolbar
* @function external:"ko.components".rich-text-editor
* @param {object} params
* @param {ko.observable<string>} params.value - the HTML being edited
* @param {ko.observable<string>} [params.direction] - 'ltr' or 'rtl'; defaults to the active language's direction
* @param {string} [params.placeholder] - shown when the editor is empty
* @param {ko.observable<boolean>} [params.disabled] - when true, the editor is read-only and the toolbar is inert
*/
export default ko.components.register('views/components/rich-text-editor', {
    viewModel: function(params) {
        const editor = new Editor({
            content: ko.unwrap(params.value) || '',
            editable: !ko.unwrap(params.disabled),
            extensions: [
                StarterKit.configure({
                    link: { openOnClick: false, HTMLAttributes: { target: null, rel: null } },
                    // don't add an empty paragraph to the end of saved content
                    trailingNode: false,
                }),
                Image.configure({ inline: true, allowBase64: false }),
                TableKit,
                Subscript,
                Superscript,
            ],
        });
        const getValue = () => editor.isEmpty ? '' : editor.getHTML();

        this.editor = editor;
        this.direction = params.direction || arches.activeLanguageDir;
        this.disabled = params.disabled;
        this.placeholder = params.placeholder;

        // keep the value and the editor in sync
        editor.on('update', () => params.value(getValue()));
        // a change from outside replaces the content without an update event, or an undo step
        const subscriptions = [params.value.subscribe((value) => {
            if ((value || '') !== getValue()) {
                editor.chain()
                    .command(({ tr }) => tr.setMeta('addToHistory', false))
                    .setContent(value || '', { emitUpdate: false })
                    .run();
            }
        })];
        if (ko.isObservable(params.disabled)) {
            subscriptions.push(params.disabled.subscribe(disabled => editor.setEditable(!disabled, false)));
        }

        // get isDisabled and isActive for each item name
        const getState = () => Object.fromEntries(Object.entries(toolbarItems).map(([name, item]) => [name, {
            isDisabled: item.isDisabled?.(editor) ?? false,
            isActive: item.isActive?.(editor) ?? false,
        }]));

        // updated after every change to the editor's content or selection
        this.state = ko.observable(getState());
        this.isEmpty = ko.observable(editor.isEmpty);
        editor.on('transaction', () => {
            this.state(getState());
            this.isEmpty(editor.isEmpty);
        });

        this.run = name => () => {
            const item = toolbarItems[name];
            if (item.action) {
                item.action(editor);
            } else {
                item.command(editor.chain().focus()).run();
            }
        };

        // link url popup
        this.linkUrl = ko.observable('');

        this.editLink = () => {
            this.linkUrl(editor.getAttributes('link').href || '');
        };

        this.applyLink = () => {
            const href = this.linkUrl().trim();
            const chain = editor.chain().focus().extendMarkRange('link');
            if (!href) {
                chain.unsetLink().run();
            } else if (editor.state.selection.empty && !editor.isActive('link')) {
                chain.insertContent({ type: 'text', text: href, marks: [{ type: 'link', attrs: { href } }] }).run();
            } else {
                chain.setLink({ href }).run();
            }
        };

        this.openLink = () => {
            if (this.linkUrl()) {
                window.open(this.linkUrl(), '_blank', 'noopener');
            }
        };

        this.removeLink = () => {
            editor.chain().focus().extendMarkRange('link').unsetLink().run();
        };

        this.imageUrl = ko.observable('');
        this.imageAlt = ko.observable('');

        this.editImage = () => {
            const { src, alt } = editor.getAttributes('image');
            this.imageUrl(src || '');
            this.imageAlt(alt || '');
        };

        this.applyImage = () => {
            const src = this.imageUrl().trim();
            if (src) {
                editor.chain().focus().setImage({ src, alt: this.imageAlt().trim() }).run();
            }
        };

        this.removeImage = () => {
            if (editor.isActive('image')) {
                editor.chain().focus().deleteSelection().run();
            }
        };

        // roving tabindex: only the most recently focused control is in the tab order
        const getControls = toolbar => Array.from(toolbar.querySelectorAll('.rich-text-editor-toolbar-button'));

        this.onFocusIn = (_data, event) => {
            const controls = getControls(event.currentTarget);
            if (controls.includes(event.target)) {
                controls.forEach((control) => { control.tabIndex = control === event.target ? 0 : -1; });
            }
            return true;
        };

        this.onKeydown = (_data, event) => {
            const controls = getControls(event.currentTarget);
            const index = controls.indexOf(document.activeElement);
            const moveTo = index === -1 ? undefined : {
                ArrowRight: (index + 1) % controls.length,
                ArrowLeft: (index - 1 + controls.length) % controls.length,
                Home: 0,
                End: controls.length - 1,
            }[event.key];
            if (moveTo !== undefined) {
                controls[moveTo].focus();
            } else if (event.key === 'Escape') {
                editor.commands.focus();
            } else {
                return true;
            }
        };

        this.dispose = () => {
            subscriptions.forEach(subscription => subscription.dispose());
            editor.destroy();
        };
    },
    template: richTextEditorTemplate,
});
