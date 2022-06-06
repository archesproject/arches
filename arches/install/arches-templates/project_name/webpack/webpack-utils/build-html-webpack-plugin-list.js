const Path = require('path');
const fs = require('fs');
const HtmlWebpackPlugin = require('html-webpack-plugin');


const _buildHtmlWebpackPluginList = function(path, outerAcc, templateDirectoryPath, javascriptDirectoryPath) {
    const list = fs.readdirSync(path).reduce((acc, name) => {
        if (fs.lstatSync(path + '/' + name).isDirectory() ) {
            return _buildHtmlWebpackPluginList(
                path + '/' + name, 
                acc,
                templateDirectoryPath
            );
        }
        else {
            const subPath = (path + '/' + name).split('/templates/')[1];
            const parsedPath = Path.parse(subPath);
            
            var filename = parsedPath['name'];
            if (parsedPath['dir']) {
               filename = parsedPath['dir'] + '/' + parsedPath['name'];
            }
            
            acc.push(new HtmlWebpackPlugin({
                template: `${templateDirectoryPath}/${filename}${parsedPath['ext']}`, // relative path to the HTML files
                filename: `templates/${filename}${parsedPath['ext']}`, // output HTML files
                chunks:  [ Path.resolve(__dirname, `${javascriptDirectoryPath}/${filename}.js`) ] // respective JS files
            }));
            return acc;
        }
    }, outerAcc);
    return list;
};

function buildHTMLWebpackPluginList(
    projectTemplateDirectoryPath, 
    projectJavascriptDirectoryPath,
    archesCoreTemplateDirectoryPath, 
    archesCoreJavascriptDirectoryPath,
) {
    const projectHtmlWebpackPluginList = _buildHtmlWebpackPluginList(
        projectTemplateDirectoryPath, 
        [],
        projectTemplateDirectoryPath, 
        projectJavascriptDirectoryPath,
    );
    const archesCoreHtmlWebpackPluginList = _buildHtmlWebpackPluginList(
        archesCoreTemplateDirectoryPath,  
        [],
        archesCoreTemplateDirectoryPath,  
        archesCoreJavascriptDirectoryPath,
    );

    const htmlWebpackPluginList = [ ...projectHtmlWebpackPluginList ];

    const projectTemplateFilenames = projectHtmlWebpackPluginList.reduce((acc, htmlWebpackPlugin) => {
        acc[htmlWebpackPlugin['userOptions']['filename']] = true;
        return acc;
    }, {});

    archesCoreHtmlWebpackPluginList.forEach(htmlWebpackPlugin => {
        if (!projectTemplateFilenames[htmlWebpackPlugin['userOptions']['filename']]) {
            htmlWebpackPluginList.push(htmlWebpackPlugin);
        }
    });

    return htmlWebpackPluginList;
};

module.exports = { buildHTMLWebpackPluginList };