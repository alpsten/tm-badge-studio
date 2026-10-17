(() => {
  const root = new URL('./', document.currentScript.src);
  const sections = window.ACHIEVEMENT_SECTIONS;
  const activeIndex = sections.findIndex(section => location.pathname.includes('/' + section.id + '/'));
  const mount = document.querySelector('[data-achievement-navigation]');
  if (!mount) return;
  const link = (text, href, className) => {
    const element = document.createElement('a');
    element.textContent = text;
    element.href = new URL(href, root).href;
    if (className) element.className = className;
    return element;
  };
  mount.className = 'achievement-navigation';
  const top = document.createElement('div');
  top.className = 'nav-top';
  top.append(link('Achievement gallery', 'index.html', 'nav-brand'), link('Badge studio', '../preview.html', 'nav-studio'));
  const nav = document.createElement('nav');
  nav.className = 'section-links';
  nav.setAttribute('aria-label', 'Achievement sections');
  const home = link('All achievements', 'index.html');
  if (activeIndex === -1) home.setAttribute('aria-current', 'page');
  nav.append(home);
  sections.forEach((section, index) => {
    const item = link(section.title, section.id + '/index.html');
    if (index === activeIndex) item.setAttribute('aria-current', 'page');
    nav.append(item);
  });
  mount.append(top, nav);
  // The menu wraps as sections are added. Keep linked headings below its actual height.
  const updateScrollOffset = () => {
    const offset = getComputedStyle(mount).position === 'sticky' ? mount.getBoundingClientRect().height + 20 : 20;
    document.documentElement.style.setProperty('--achievement-nav-offset', offset + 'px');
  };
  new ResizeObserver(updateScrollOffset).observe(mount);
  updateScrollOffset();
  if (activeIndex !== -1) {
    const pager = document.createElement('nav');
    pager.className = 'achievement-pager';
    pager.setAttribute('aria-label', 'Previous and next achievement section');
    const previous = sections[activeIndex - 1];
    const next = sections[activeIndex + 1];
    pager.append(previous ? link(previous.title, previous.id + '/index.html') : link('All achievements', 'index.html'));
    pager.append(next ? link(next.title, next.id + '/index.html', 'next') : link('All achievements', 'index.html', 'next'));
    document.querySelector('main').append(pager);
  }

  // Keep the comparison settings when moving between the hub and sections.
  const key = 'tm-achievement-preview';
  const controls = ['view', 'center', 'frame', 'background'];
  const read = () => { try { return JSON.parse(localStorage.getItem(key)) || {}; } catch { return {}; } };
  document.addEventListener('DOMContentLoaded', () => {
    const saved = read();
    for (const id of controls) {
      const select = document.getElementById(id);
      if (!select) continue;
      if (Array.from(select.options).some(option => option.value === saved[id])) {
        select.value = saved[id];
        select.dispatchEvent(new Event('change'));
      }
      select.addEventListener('change', () => {
        try { localStorage.setItem(key, JSON.stringify({...read(), [id]: select.value})); } catch { /* Preview remains usable without storage. */ }
      });
    }
    if (location.hash) requestAnimationFrame(() => {
      try { document.getElementById(decodeURIComponent(location.hash.slice(1)))?.scrollIntoView(); } catch { /* Ignore malformed fragments. */ }
    });
  });
})();
