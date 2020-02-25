
# subtag
[Language tag](https://www.w3.org/International/articles/language-tags/) parser. Parse language tags into subtags.

## api
- <b>`subtag(tag)`</b> parse tag into [subtags object](#objects)
- <b>`subtag.split(tag)`</b> split tag into [subtags array](#arrays)
- <b>`subtag.language(tag)`</b> get [primary language subtag](https://www.w3.org/International/articles/language-tags/#language)
- <b>`subtag.extlang(tag)`</b> get [extended language subtag](https://www.w3.org/International/articles/language-tags/#extlang)
- <b>`subtag.script(tag)`</b> get [script subtag](https://www.w3.org/International/articles/language-tags/#script)
- <b>`subtag.region(tag)`</b> get [region subtag](https://www.w3.org/International/articles/language-tags/#region)

### notes
- parsing is done via regex
- unpresent subtags will be an empty string
- separator can be dashes (standard) or underscores

## setup
### install via npm or yarn
```
npm install subtag --save
```

```
yarn add subtag
```

## usage
### `require` usage
```js
var subtag = require('subtag')
```

### `import` usage
```js
import subtag from 'subtag'
```

### examples

#### objects

```js
subtag('ja-JP') // {language: 'ja', extlang: '', script: '', region: 'JP'}
subtag('es-AR') // {language: 'es', extlang: '', script: '', region: 'AR'}
```

#### arrays

```js
subtag.split('yue') // ["yue"]
subtag.split('es-419') // ["es", "419"]
subtag.split('zh-Hant-HK') // ["zh", "Hant", "HK"]
subtag.split('en-90210') // ["en"] because 90210 is fake
```

#### subtags

```js
subtag.language('en') // 'en'
subtag.extlang('en') // ''
subtag.script('en') // ''
subtag.region('en') // ''

subtag.language('en-US') // 'en'
subtag.extlang('en-US') // ''
subtag.script('en-US') // ''
subtag.region('en-US') // 'US'

subtag.language('zh-yue') // 'zh'
subtag.extlang('zh-yue') // 'yue'
subtag.script('zh-yue') // ''
subtag.region('zh-yue') // ''

subtag.language('zh-Hans') // 'zh'
subtag.extlang('zh-Hans') // ''
subtag.script('zh-Hans') // 'Hans'
subtag.region('zh-Hans') // ''
```

## structure
[language<b>-</b>extlang<b>-</b>script<b>-</b>region<b>-</b>variant<b>-</b>extension<b>-</b>privateuse](https://www.w3.org/International/articles/language-tags/#rfc)

<table>
<tr>
  <th scope="col">type</th>
  <th scope="col">pattern</th>
  <th scope="col">convention</th>
</tr>
<tr>
  <td>language</td>
  <td>2-letter or 3-letter</td>
  <td>lowercase</td>
</tr>
<tr>
  <td>extlang</td>
  <td>3-letter</td>
  <td>lowercase</td>
</tr>
<tr>
  <td>script</td>
  <td>4-letter</td>
  <td>titlecase</td>
</tr>
<tr>
  <td>region</td>
  <td>2-letter or 3-number</td>
  <td>uppercase</td>
</tr>
</table>

### `.pattern`
Regex patterns are exposed for validation

```js
subtag.language.pattern.test('en') // true
subtag.language.pattern.test('ast') // true
subtag.language.pattern.test('fake') // false
subtag.extlang.pattern.test('yue') // true
subtag.script.pattern.test('Hans') // true
subtag.region.pattern.test('US') // true
subtag.region.pattern.test('005') // true
subtag.region.pattern.test('90210') // false
```

## compatibility
Works in Node.js and ES5+ browsers
