(function ($) {
  'use strict';

  $.fn.validate = function (options) {
    
    var defaults = {
      messageRequired: 'Required',
      messageEmail: 'Invalid Email',
      validateEmail: true,
      ajax: false,
      callback: function () {}
    };

    var settings = $.extend({}, defaults, options);
    var $form = this;
    var $inputs = $form.find('[data-validate]');
    var regex = /^.+@.+\..+$/;
    var inputType;
    var validForm;

    // Init DOM
    $inputs.after('<span class="validate-message" />');

    // Validation fail
    function validationFail (input, message) {
      $(input).addClass('validate-error');
      $(input).next().text(message);
      validForm = false;
    }

    // Validation pass
    function validationPass (input) {
      $(input).removeClass('validate-error');
      $(input).next().text('');
    }

    // Validate email
    function validateEmail (email) {
      return regex.test(email);
    }

    // Check input instance
    function checkInput (input) {
      inputType = $(input).attr('type');

      if (!input.value) {
        // No value
        validationFail(input, settings.messageRequired);
      } else if (inputType === 'email' && settings.validateEmail) {
        // Check email validation
        if (!validateEmail(input.value)) {
          validationFail(input, settings.messageEmail);
        } else {
          validationPass(input);
        }
      } else {
        // Passes validation
        validationPass(input);
      }
    }

    // Validate all inputs
    function runValidation (form) {
      validForm = true;
      $inputs.each(function () {
        checkInput(this);
      });
    }

    // Keyup event - only runs after a submit attempt
    $(document).on('keyup', $form.selector + '[data-submitted] [data-validate]', function () {
      checkInput(this);
    });
    
    // Submit event
    $form.on('submit', function (event) {
      event.preventDefault();

      // Add `data-submitted` attribute to form
      $(this).attr('data-submitted', '');

      // Validate form
      runValidation(this);

      // Check if form valid
      if (validForm) {
        if (settings.ajax) {
          // Callback
          settings.callback.call(this);
        } else {
          // Submit
          this.submit();
        }
      } else {
        // Failed validation
        // Bring focus to input
        $('.validate-error:first').focus();
        return false;
      }

    });
   
  };

}(jQuery));