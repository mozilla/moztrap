$(function() {
  $('ul.envlist').formset({
    prefix: '{{ form.env_formset.prefix }}',
    formTemplate: '#empty-env-form > li',
    formCssClass: 'env-form',
    deleteCssClass: 'remove',
    deleteText: 'removefields',
    addCssClass: 'addfields',
    addText: 'add environment constraints »'
  });
})