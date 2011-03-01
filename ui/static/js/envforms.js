$(function() {
  $('ul.envlist').formset({
    prefix: '{{ form.env_formset.prefix }}',
    formTemplate: '#empty-env-form > li',
    formCssClass: 'env-form',
    deleteCssClass: 'removefields',
    deleteText: 'remove',
    addCssClass: 'addfields',
    addText: 'add environment constraints »'
  });
})