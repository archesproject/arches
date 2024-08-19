const Path = require('path');
const fs = require('fs');

function buildFilepathLookup(path, staticUrlPrefix) {
    if (!fs.existsSync(path)) {
        return;
    }

    const prefix = path.match(/[^/]+$/);
    const staticUrl = staticUrlPrefix ? staticUrlPrefix : "";

    const getFileList = function (dirPath) {
        return fs.readdirSync(dirPath, { withFileTypes: true }).reduce((fileList,entries) => {
            const childPath = Path.join(dirPath, entries.name);

            if (entries.isDirectory()) {
                fileList.push(...getFileList(childPath, fileList));
            } else
            {
                fileList.push(childPath);
            }
            return fileList;
        }, []);
    };

    return getFileList(path).reduce((lookup, file) => {
        // Ignore dotfiles
        if (file.match(new RegExp(Path.sep + '\\.')) || file.match(/^\./)) {
            return lookup;
        }
        const extension = file.match(/[^.]+$/).toString();
        if (extension === 'js') {
            lookup[file.replace(path,'').replace(/\\/g, '/').replace(/\.js$/,'').replace(/^\//,'')] = {"import": file, "filename": `${prefix}/[name].${extension}`};
        }
        else
        {
            // staticUrl used for images
            lookup[`${staticUrl}${prefix}/${file.replace(path,'').replace(/\\/g, '/').replace(/^\//,'')}`] = file;
        }
        return lookup;
    }, {});
}

module.exports = { buildFilepathLookup };
