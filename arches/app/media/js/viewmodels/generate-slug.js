define([
  'jquery',
  'underscore',
  'knockout',
  'knockout-mapping',
  'arches',
  'uuid',
  'templates/views/viewmodels/generate-slug.htm'
], function ($, _, ko, koMapping, arches, uuid, template) {
  const GenerateSlug = function (params) {
    this.rawText = params?.rawText || ko.observable('');
    this.slug = params?.slug || ko.observable('');
    this.autoGenerate = params?.autoGenerate || ko.observable(true);
    this.suffix = ko.observable(params?.suffix) || ko.observable('');
    this.radioLabel = params?.radioLabel || 'Auto generate slug?';
    this.textLabel = params?.textLabel || 'Auto Generated Slug';

    this.rawText.subscribe(() => {
      if (this.autoGenerate()) {
        this.slug(this.createSlug());
      }
    });

    this.slug.subscribe(() => {
      this.autoGenerate(this.isAutoGenerateActive());
    });

    this.isAutoGenerateActive = () => {
      return this.slug() === this.createSlug();
    };

    this.createSlug = () => {
      const suffix = this.suffix() ? `-${this.suffix()}` : '';
      return this.rawText().toLowerCase().split(' ').join('-') + suffix;
    };

    this.init = () => {
      this.slug(this.createSlug());
    };

    this.init();
  };

  ko.components.register('generate-slug', {
    template: template,
    viewModel: GenerateSlug
  });

  return GenerateSlug;
});
