/* Retain legacy form plugins, while sharing the Lab interaction treatment. */
(() => {
  const init = (root = document) => {
    if (window.jQuery?.fn.select2) {
      window.jQuery(root).find('select.select2').addBack('select.select2').each(function () {
        if (!this.classList.contains('select2-hidden-accessible')) {
          window.jQuery(this).select2({theme: 'bootstrap-5', width: '100%'});
        } else {
          window.jQuery(this).trigger('change.select2');
        }
      });
    }
    window.lucide?.createIcons();
  };
  document.addEventListener('DOMContentLoaded', () => init());
  document.addEventListener('htmx:afterSwap', event => init(event.detail.target));
  document.addEventListener('htmx:afterRequest', event => {
    const field = event.detail.elt?.querySelector?.('textarea[name="content"]');
    if (!field || !field.closest('.message-input-container')) return;
    const status = field.form.querySelector('.message-status');
    if (status) status.hidden = !!event.detail.successful;
    if (!event.detail.successful) return;
    field.value = '';
    field.dispatchEvent(new Event('input', {bubbles: true}));
  });
  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape') return;
    document.querySelectorAll('.account-navigation[open], .mobile-navigation[open]').forEach(menu => {
      menu.open = false;
      menu.querySelector('summary')?.focus();
    });
  });
})();
