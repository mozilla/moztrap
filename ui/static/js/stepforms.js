$(function() {
  $('ol.steplist').formset({
    prefix: '{{ form.steps_formset.prefix }}',
    formTemplate: '#empty-step-form > li',
    formCssClass: 'steps-form',
    deleteCssClass: 'removefields',
    deleteText: 'remove',
    deleteOnlyNew: true,
    addCssClass: 'addfields',
    addText: 'add a step »'
  });
})