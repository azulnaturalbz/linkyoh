(() => {
  const icons = () => window.lucide?.createIcons();
  icons();
  for (const filters of document.querySelectorAll('[data-expand-desktop="true"]')) {
    filters.open = window.matchMedia('(min-width: 1000px)').matches;
  }
  document.body.addEventListener('htmx:afterSwap', icons);
  const menu = document.querySelector('.mobile-navigation');
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && menu?.open) {
      menu.open = false;
      menu.querySelector('summary').focus();
    }
  });
  document.addEventListener('click', (event) => {
    if (menu?.open && !menu.contains(event.target)) menu.open = false;
  });
  for (const [parentId, childId] of [['category', 'subcategory'], ['district', 'location']]) {
    const parent = document.getElementById(parentId);
    const child = document.getElementById(childId);
    if (!parent || !child) continue;
    const constrain = (changed) => {
      if (changed) child.value = '';
      for (const option of child.options) {
        const unavailable = Boolean(option.value && parent.value && option.dataset.parent !== parent.value);
        option.hidden = unavailable && !option.selected;
        option.disabled = unavailable && !option.selected;
      }
    };
    parent.addEventListener('change', () => constrain(true));
    constrain(false);
  }
})();
