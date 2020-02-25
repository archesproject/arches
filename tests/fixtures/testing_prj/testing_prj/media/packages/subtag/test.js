!function() {
  var api = require('./')
  var dash = '-'
  var score = '_'

  function format(s, glue) {
    return s.replace(/[_-]+/g, glue)
  }

  function test(object) {
    try {
      if (api.split(object.tag).join(dash) !== object.valid) throw new Error('Fail: split() for ' + object.tag)
      if (api.language(object.tag) !== object.language) throw new Error('Fail: language for ' + object.tag)
      if (api.extlang(object.tag) !== object.extlang) throw new Error('Fail: extlang for ' + object.tag)
      if (api.script(object.tag) !== object.script) throw new Error('Fail: script for ' + object.tag)
      if (api.region(object.tag) !== object.region) throw new Error('Fail: region for ' + object.tag)
      if (api.language(object.tag) !== api(object.tag).language) throw new Error('Fail: language() for ' + object.tag)
      if (api.extlang(object.tag) !== api(object.tag).extlang) throw new Error('Fail: extlang() for ' + object.tag)
      if (api.script(object.tag) !== api(object.tag).script) throw new Error('Fail: script() for ' + object.tag)
      if (api.region(object.tag) !== api(object.tag).region) throw new Error('Fail: region() for ' + object.tag)
    } catch(e) {
      console.warn('parse:', object.tag, JSON.stringify(api(object.tag)))
      throw e
    }
    console.log('Pass: ', object.tag)
  }

  var tests = [
    {
      tag: '',
      language: '',
      extlang: '',
      script: '',
      region: ''
    },
    {
      tag: 'ast',
      language: 'ast',
      extlang: '',
      script: '',
      region: '',
    },
    {
      tag: 'en',
      language: 'en',
      extlang: '',
      script: '',
      region: ''
    },
    {
      tag: 'en-US',
      language: 'en',
      extlang: '',
      script: '',
      region: 'US'
    },
    {
      tag: 'kam-KE',
      language: 'kam',
      extlang: '',
      script: '',
      region: 'KE'
    },
    {
      tag: 'gsw-LI',
      language: 'gsw',
      extlang: '',
      script: '',
      region: 'LI'
    },
    {
      tag: 'es-005',
      language: 'es',
      extlang: '',
      script: '',
      region: '005'
    },
    {
      tag: 'zh-yue',
      language: 'zh',
      extlang: 'yue',
      script: '',
      region: ''
    },
    {
      tag: 'is-red-OK',
      language: 'is',
      extlang: 'red',
      script: '',
      region: 'OK'
    },
    {
      tag: 'are-you-007',
      language: 'are',
      extlang: 'you',
      script: '',
      region: '007'
    },
    {
      valid: 'en',
      tag: 'en-90210',
      language: 'en',
      extlang: '',
      script: '',
      region: ''
    },
    {
      tag: 'zh-Hans',
      language: 'zh',
      extlang: '',
      script: 'Hans',
      region: ''
    },
    {
      tag: 'zh-Hant-HK',
      language: 'zh',
      extlang: '',
      script: 'Hant',
      region: 'HK'
    },
    {
      tag: 'is-This-007',
      language: 'is',
      extlang: '',
      script: 'This',
      region: '007'
    },
    {
      tag: 'pa-Guru-IN',
      language: 'pa',
      extlang: '',
      script: 'Guru',
      region: 'IN'
    },
    {
      tag: 'is-the-Expr',
      language: 'is',
      extlang: 'the',
      script: 'Expr',
      region: ''
    },
    {
      tag: 'is-the-Expr-OK',
      language: 'is',
      extlang: 'the',
      script: 'Expr',
      region: 'OK'
    },
    {
      tag: 'is-the-case-007',
      language: 'is',
      extlang: 'the',
      script: 'case',
      region: '007'
    }
  ].map(function(o) {
    if (!o.hasOwnProperty('valid')) o.valid = format(o.tag, dash)
    return o
  })

  tests.forEach(test)
  tests.map(function(o) {
    o = Object.assign({}, o)
    o.tag = format(o.tag, score)
    return o
  }).forEach(test)

  console.log('All tests passed :)')
}();
