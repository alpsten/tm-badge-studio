(() => {
  const root = new URL('./', document.currentScript.src);
  const byId = id => document.getElementById(id);
  const sections = window.ACHIEVEMENT_SECTIONS;
  const groups = [];
  const compositions = [];
  const fullImageThumbs = [];
  for (const section of sections) byId('section').add(new Option(section.title, section.id));
  const image = (path, className) => {
    const element = new Image();
    element.src = new URL(path, root).href;
    element.className = className;
    element.alt = '';
    element.draggable = false;
    element.decoding = 'async';
    return element;
  };
  function refreshArtwork() {
    const symbolOnly = byId('view').value === 'symbol';
    for (const {composition, center, frame, emblem, thumb, item} of compositions) {
      composition.classList.toggle('symbol-only', symbolOnly);
      center.src = new URL('../512/modular/centers/' + byId('center').value + '.webp', root).href;
      const finish = byId('frame').value === 'auto' ? (item.preferredFrame || 'gold') : byId('frame').value;
      frame.src = new URL('../512/modular/frames/' + finish + '.webp', root).href;
      const placement = symbolOnly ? item.symbolPlacement : item.badgePlacement;
      for (const property of ['left', 'top', 'width', 'height']) emblem.style[property] = placement[property] + '%';
      thumb.dataset.background = byId('background').value;
    }
    for (const thumb of fullImageThumbs) thumb.dataset.background = byId('background').value;
    byId('center').disabled = symbolOnly;
    byId('frame').disabled = symbolOnly;
  }
  function filter() {
    const words = byId('search').value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    const selected = byId('section').value;
    let total = 0, visibleSections = 0;
    for (const group of groups) {
      let count = 0;
      for (const card of group.cards) {
        const visible = (selected === 'all' || selected === group.section.id) && words.every(word => card.search.includes(word));
        card.element.hidden = !visible;
        if (visible) count++;
      }
      group.element.hidden = !count;
      group.count.textContent = count;
      total += count;
      if (count) visibleSections++;
    }
    byId('summary').textContent = total + (total === 1 ? ' achievement' : ' achievements') + ' · ' + visibleSections + (visibleSections === 1 ? ' section' : ' sections');
    byId('empty').hidden = total !== 0;
    const url = new URL(location.href);
    url.searchParams.delete('q'); url.searchParams.delete('section');
    if (byId('search').value.trim()) url.searchParams.set('q', byId('search').value.trim());
    if (selected !== 'all') url.searchParams.set('section', selected);
    history.replaceState(null, '', url);
  }
  function addSection(section, items) {
    const element = document.createElement('section');
    element.className = 'achievement-section';
    element.id = section.id;
    const heading = document.createElement('div');
    heading.className = 'section-heading';
    const title = document.createElement('h2');
    title.textContent = section.title;
    title.id = section.id + '-title';
    element.setAttribute('aria-labelledby', title.id);
    const count = document.createElement('span');
    count.className = 'count';
    title.append(count);
    const open = document.createElement('a');
    open.href = new URL(section.id + '/index.html', root).href;
    open.textContent = 'Open section';
    open.setAttribute('aria-label', 'Open ' + section.title);
    heading.append(title, open);
    const grid = document.createElement('div');
    grid.className = 'achievement-grid';
    const cards = [];
    for (const item of items) {
      const card = document.createElement('a');
      card.className = 'achievement-card';
      card.href = new URL(section.id + '/index.html#' + item.id, root).href;
      const thumb = document.createElement('div');
      thumb.className = 'thumb';
      const composition = document.createElement('div');
      composition.className = 'composition';
      if (item.fullImage) {
        composition.append(image(section.id + '/' + item.file + '?v=' + item.sourceSha256.slice(0, 12), 'base'));
        fullImageThumbs.push(thumb);
      } else {
        const center = image('../512/modular/centers/black.webp', 'base center');
        const frame = image('../512/modular/frames/' + (item.preferredFrame || 'gold') + '.webp', 'base frame');
        const emblem = image(section.id + '/' + item.file + '?v=' + item.sourceSha256.slice(0, 12), 'emblem');
        composition.append(center, frame, emblem);
        compositions.push({composition, center, frame, emblem, thumb, item});
      }
      thumb.append(composition);
      const copy = document.createElement('div');
      copy.className = 'card-copy';
      const name = document.createElement('h3');
      name.textContent = item.name;
      const description = document.createElement('p');
      description.textContent = item.description;
      copy.append(name, description);
      card.append(thumb, copy);
      grid.append(card);
      cards.push({element: card, search: [section.title, item.name, item.description].join(' ').toLocaleLowerCase()});
    }
    element.append(heading, grid);
    byId('sections').append(element);
    groups.push({element, section, cards, count});
  }
  const query = new URLSearchParams(location.search);
  byId('search').value = query.get('q') || '';
  if (sections.some(section => section.id === query.get('section'))) byId('section').value = query.get('section');
  byId('search').addEventListener('input', filter);
  byId('section').addEventListener('change', filter);
  byId('clear').addEventListener('click', () => { byId('search').value = ''; byId('section').value = 'all'; filter(); byId('search').focus(); });
  for (const id of ['view', 'center', 'frame', 'background']) byId(id).addEventListener('change', refreshArtwork);
  const load = section => new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = new URL(section.id + '/concepts.js?v=cross-four-v14', root).href;
    script.onload = () => Array.isArray(window[section.data]) ? resolve(window[section.data]) : reject(new Error(section.title));
    script.onerror = () => reject(new Error(section.title));
    document.head.append(script);
  });
  Promise.allSettled(sections.map(load)).then(results => {
    const failed = [];
    results.forEach((result, index) => {
      if (result.status === 'fulfilled') addSection(sections[index], result.value);
      else failed.push(sections[index].title);
    });
    if (failed.length) { byId('load-error').hidden = false; byId('load-error').textContent = 'Could not load: ' + failed.join(', ') + '. Reload to try again.'; }
    refreshArtwork(); filter();
    document.documentElement.dataset.ready = 'true';
  });
})();
