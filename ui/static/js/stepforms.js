$(function() {
  $('ol.steplist').formset({
    prefix: '{{ form.steps_formset.prefix }}',
    formTemplate: '#empty-step-form > li',
    formCssClass: 'steps-form',
    deleteCssClass: 'remove',
    deleteText: 'removefields',
    deleteOnlyNew: true,
    addCssClass: 'addfields',
    addText: 'add a step »'
  });
})