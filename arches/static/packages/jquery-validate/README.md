# jQuery Validate

A lightweight jQuery plugin for form validation

### Demo:
https://ryanlittle.github.io/jquery-validate

---

## Usage:

- Ensure that you have jQuery in your project

  ```html
  <script src="//ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
  ```

- Add the validate.js file to your project

  ```html
  <script src="validate.min.js"></script>
  ```

- Set up your form(s), adding a `data-validate` attribute to the fields you want to validate

  ```html
  <form id="form" action="" method="post">
    <input type="text" name="Name" data-validate>
    <input type="email" name="Email" data-validate>
    <textarea name="Message" data-validate></textarea>
    <input type="submit">
  </form>
  ```

  To validate an email address, the input needs to have `type="email"`.

- Initialize the plugin with `.validate()`

  ```javascript
  $('#form').validate();
  ```

  You could also override some default options:

  ```javascript
  $('#form').validate({
    messageRequired: 'Required',
    messageEmail: 'Invalid Email',
    validateEmail: true,
    ajax: false,
    callback: function () {}
  });
  ```

- Optionally, add CSS styles for the validate elements:

  ```css
  /* Class added to error input elements */
  .validate-error {
    border-color: #d50000;
  }

  /* Error messsages */
  .validate-message {
    color: #d50000;
  }
  ```

  To keep the plugin simple, there is no CSS included.

---

## Reference:

### AJAX and callback

`ajax: true` needs to be set in order for the callback function to be invoked. For the callback function, you can add your AJAX submission. Within the callback, you have access to the form through the `this` keyword:

```javascript
$('#form').validate({
  ajax: true,
  callback: function () {
    $.ajax({
      url: '', 
      type: 'POST',
      data: $(this).serialize(),
      dataType: 'json'
    });
  }
});
```

### Message Placement

The error messages are added immediately after each input as `<span class="validate-message">` elements. You could choose to wrap your inputs in containing elements, and the `<span>` elements would also get contained.

Input:
```html
<div>
  <input type="text" name="Name" data-validate>
</div>
```

Output:
```html
<div>
  <input type="text" name="Name" data-validate>
  <span class="validate-message"></span>
</div>
```

---

## License:

[MIT](http://opensource.org/licenses/MIT)