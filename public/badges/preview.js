const palette = window.BADGE_CORPORATIONS;
const corporations = new Map(palette.corporations.map(corp => [corp.id, corp]));
const logos = new Map(window.BADGE_LOGOS.logos.map(logo => [logo.corporation, logo]));
const byId = id => document.getElementById(id);
const value = id => byId(id).value;
const colorName = key => palette.colors[key]?.label ?? key;
const assetVersion = 'corporations-kuiper-manutech-v12';
const distinctMode = () => value('palette-mode') === 'distinct';
const variantsFor = corp => distinctMode() ? [corp.distinct_variant] : corp.variants;
const activeDuplicates = () => distinctMode() ? palette.distinct_duplicates : palette.duplicates;
const tierNames = { plate: 'Plate', 'crest-only': 'Crest only', 'small-wings': 'Small wings', 'small-wings-crest': 'Small wings + Crest', wings: 'Ascendant wings', crest: 'Ascendant wings + Crest' };
const ornaments = { plate: [], 'crest-only': ['crest'], 'small-wings': ['wings-small'], 'small-wings-crest': ['wings-small', 'crest'], wings: ['wings'], crest: ['wings', 'crest'] };
const selectedStyle = (wings, crest) => wings === 'small' ? (crest ? 'small-wings-crest' : 'small-wings') : wings === 'ascendant' ? (crest ? 'crest' : 'wings') : (crest ? 'crest-only' : 'plate');
let activePanel = 'mixer';
let galleryDirty = true;

byId('metal').replaceChildren();
for (const key of palette.center_colors) byId('color').add(new Option(colorName(key), key, false, key === 'black'));
for (const key of palette.finish_colors) {
  byId('metal').add(new Option(colorName(key), key, false, key === 'gold'));
  for (const id of ['outer-color', 'wing-color', 'crest-color']) byId(id).add(new Option(colorName(key), key));
}
for (const corp of palette.corporations) byId('corporation').add(new Option(corp.name, corp.id));
for (const logo of logos.values()) byId('logo').add(new Option(logo.name, logo.corporation));

function selection() {
  const corp = corporations.get(value('corporation'));
  return corp ? { corp, variant: variantsFor(corp)[Number(value('variant')) || 0] } : null;
}

function setCorporation(id, index = 0) {
  byId('corporation').value = corporations.has(id) ? id : 'custom';
  const corp = corporations.get(id);
  if (corp) byId('logo').value = 'auto';
  byId('variant').replaceChildren();
  if (corp) variantsFor(corp).forEach((variant, number) => byId('variant').add(new Option(variant.label, String(number), false, number === index)));
  byId('variant-label').hidden = !corp || variantsFor(corp).length < 2;
  byId('edit-colors').hidden = !corp;
  document.querySelectorAll('.custom-choice').forEach(label => { label.hidden = Boolean(corp); });
}

function settings() {
  return { tier: selectedStyle(value('wings'), value('crest') === 'on'), resolution: value('resolution'), rank: value('rank'), border: value('border') === 'on', outerColor: value('outer-color'), wingColor: value('wing-color'), crestColor: value('crest-color'), accents: value('accents') === 'on', showLogos: value('show-logos') === 'on', logo: value('logo'), logoScale: Number(value('logo-scale')), logoContrast: value('logo-contrast') };
}

function selectedLogo(preset, options) {
  return options.showLogos ? logos.get(options.logo === 'auto' ? preset?.corp.id : options.logo) ?? null : null;
}

function updateLogoHelp() {
  const options = settings();
  const preset = selection();
  const logo = selectedLogo(preset, options);
  byId('logo-help').textContent = !options.showLogos ? 'Logos are hidden. Your selection is kept for when you turn them back on.'
    : activePanel === 'corporations' ? `${logos.size} corporation logos available. The gallery always matches each logo to its corporation.`
    : logo ? `${logo.name} logo · ${logo.keep_original_square ? 'Original square artwork preserved.' : 'Original colors, fitted inside the frame.'}`
    : preset ? `No logo added for ${preset.corp.name} yet. Choose one above to experiment, or try a corporation with a logo.`
    : 'Choose a logo above, or select a corporation to use its matching logo.';
}

function drawBadge(badge, options, preset = null, lazy = false) {
  const { tier, resolution, rank, border, accents, outerColor } = options;
  const frame = preset?.variant.frame ?? value('metal');
  const center = preset?.variant.center ?? value('color');
  const root = palette.ornament_roots[frame];
  const accent = accents && preset ? preset.corp.suggested_accent : null;
  const accentRoot = accent ? palette.ornament_roots[accent] : root;
  const wingColor = options.wingColor === 'auto' ? frame : options.wingColor;
  const crestColor = options.crestColor === 'auto' ? accent || frame : options.crestColor;
  const wingRoot = palette.ornament_roots[wingColor];
  const crestRoot = palette.ornament_roots[crestColor];
  const borderRoot = outerColor && outerColor !== 'auto' ? palette.ornament_roots[outerColor] : accentRoot;
  const parts = ornaments[tier].map(name => name.startsWith('wings') && border ? `${name}-border` : name);
  if (border) parts.splice(parts.includes('crest') ? parts.indexOf('crest') : parts.length, 0, 'outer-border');
  const paths = parts.map(name => `${name === 'outer-border' ? borderRoot : name === 'crest' ? crestRoot : wingRoot}/${name}.webp`);
  if (preset) paths.push(preset.variant.badge);
  else paths.push(palette.modular_centers[center], palette.modular_frames[frame]);
  const logo = selectedLogo(preset, options);
  if (logo) paths.push(logo.path);
  paths.push(`${accentRoot}/bottom-plate.webp`, `${accentRoot}/rank-${rank}.webp`);
  badge.replaceChildren(...paths.map(path => {
    const image = document.createElement('img');
    image.src = `${resolution}/${path}?v=${assetVersion}`;
    image.alt = '';
    image.width = Number(resolution);
    image.height = Number(resolution);
    if (path === logo?.path) {
      image.className = 'corporation-logo';
      image.dataset.contrast = options.logoContrast;
      image.style.setProperty('--logo-scale', options.logoScale);
    }
    if (lazy) image.loading = 'lazy';
    return image;
  }));
  badge.setAttribute('aria-label', [
    ...(preset ? [preset.corp.name] : []),
    ...(logo ? [`${logo.name} logo`] : []),
    `${colorName(center)} center`, `${colorName(frame)} frame`, tierNames[tier],
    ...(parts.some(name => name.startsWith('wings')) ? [`${colorName(wingColor)} wings`] : []),
    ...(parts.includes('crest') ? [`${colorName(crestColor)} crest`] : []),
    ...(accent ? [`suggested ${colorName(accent)} accent`] : []),
    border ? `${colorName(outerColor !== 'auto' ? outerColor : accent || frame)} outer border` : 'without outer border',
    `milestone ${rank}`,
  ].join(', '));
  return paths.length;
}

function swatch(key, role) {
  const item = document.createElement('span');
  item.className = 'swatch';
  const dot = document.createElement('i');
  dot.style.backgroundColor = palette.colors[key].hex;
  dot.setAttribute('aria-hidden', 'true');
  item.append(dot, document.createTextNode(`${role}: ${colorName(key)}`));
  return item;
}

function paletteLabels(preset, options) {
  const labels = [swatch(preset.variant.center, 'Center'), swatch(preset.variant.frame, 'Frame')];
  if (options.accents && preset.corp.suggested_accent) labels.push(swatch(preset.corp.suggested_accent, 'Suggested accent'));
  if (ornaments[options.tier].some(name => name.startsWith('wings')) && options.wingColor !== 'auto') labels.push(swatch(options.wingColor, 'Wings'));
  if (ornaments[options.tier].includes('crest') && options.crestColor !== 'auto') labels.push(swatch(options.crestColor, 'Crest'));
  if (options.border && options.outerColor !== 'auto') labels.push(swatch(options.outerColor, 'Outer border'));
  return labels;
}

function update() {
  const options = settings();
  const preset = selection();
  byId('outer-color').disabled = !options.border;
  byId('wing-color').disabled = value('wings') === 'none';
  byId('crest-color').disabled = value('crest') === 'off';
  for (const id of ['logo', 'logo-scale', 'logo-contrast']) byId(id).disabled = !options.showLogos;
  updateLogoHelp();
  updatePaletteHelp();
  const badge = byId('badge');
  const count = drawBadge(badge, options, preset);
  badge.style.setProperty('--display', `${value('display')}px`);
  byId('palette-summary').replaceChildren(...(preset ? paletteLabels(preset, options) : []));
  byId('palette-summary').hidden = !preset;
  byId('palette-reason').hidden = !(distinctMode() && preset?.corp.distinct_changed);
  byId('palette-reason').textContent = preset?.corp.distinct_palette?.reason ?? '';
  byId('status').textContent = `${preset ? preset.corp.name + ' · ' : ''}${count} aligned WebP layers · ${options.resolution} px source · ${value('display')} px display`;
  const duplicate = preset && activeDuplicates().find(group => group.center === preset.variant.center && group.frame === preset.variant.frame);
  byId('duplicate-note').textContent = duplicate ? `This original pair is also used by ${duplicate.corporations.filter(name => name !== preset.corp.name).join(', ')}. Switch to Distinct colors to compare the revised palettes.` : '';
  for (const example of document.querySelectorAll('[data-tier]')) drawBadge(example, { ...options, tier: example.dataset.tier }, preset);
  for (const image of document.querySelectorAll('[data-award]')) image.src = `${options.resolution}/awards/${image.dataset.award}.webp?v=${assetVersion}`;
  for (const surface of document.querySelectorAll('.surface')) surface.classList.toggle('light', value('background') === 'light');
  galleryDirty = true;
  if (activePanel === 'corporations') renderGallery();
}

function updatePaletteHelp() {
  byId('show-alternatives').disabled = distinctMode();
  byId('palette-help').textContent = distinctMode()
    ? `${palette.corporation_count} unique center / frame pairs · ${palette.distinct_changed_count} revised palettes. Original colors remain available for comparison.`
    : `Original colors · ${palette.variant_count} combinations including slash-color alternatives. Switch to Distinct colors to compare the proposals.`;
  const groups = activeDuplicates();
  byId('duplicate-summary').textContent = groups.length ? `Repeated original pairs · ${groups.length} groups, including alternatives` : 'No repeated center / frame pairs';
  byId('duplicate-list').replaceChildren(...groups.map(group => {
    const item = document.createElement('li');
    item.textContent = `${colorName(group.center)} / ${colorName(group.frame)}: ${group.corporations.join(', ')}`;
    return item;
  }));
  byId('duplicate-help').textContent = distinctMode()
    ? 'Every corporation has a different center / frame pair in this proposal. Related colors can still look similar; logos and names help identify each corporation.'
    : 'These repeats are kept in Original colors. Distinct colors provides one unique center / frame pair per corporation.';
}

function renderGallery() {
  const query = value('corporation-search').toLowerCase().trim();
  const showAlternatives = !distinctMode() && byId('show-alternatives').checked;
  const options = { ...settings(), logo: 'auto' };
  const cards = [];
  let count = 0;
  let withLogos = 0;
  for (const corp of palette.corporations) {
    const available = variantsFor(corp);
    const searchable = [corp.name, ...available.flatMap(variant => [colorName(variant.center), colorName(variant.frame)])].join(' ').toLowerCase();
    if (query && !searchable.includes(query)) continue;
    if (byId('logos-only').checked && !logos.has(corp.id)) continue;
    if (byId('changed-only').checked && !corp.distinct_changed) continue;
    count++;
    if (logos.has(corp.id)) withLogos++;
    const variants = showAlternatives ? available : available.slice(0, 1);
    variants.forEach((variant, index) => {
      const preset = { corp, variant };
      const card = document.createElement('article');
      card.className = 'surface corporation-card';
      card.classList.toggle('light', value('background') === 'light');
      const badge = document.createElement('div');
      badge.className = 'badge';
      badge.setAttribute('role', 'img');
      drawBadge(badge, options, preset, true);
      const title = document.createElement('h3');
      title.textContent = corp.name;
      const labels = document.createElement('div');
      labels.className = 'palette-labels';
      labels.append(...paletteLabels(preset, options));
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = showAlternatives ? 'Open this combination' : available.length > 1 ? `Open · ${available.length} alternatives` : 'Open in mixer';
      button.addEventListener('click', () => { setCorporation(corp.id, index); setPanel('mixer'); update(); byId('corporation').focus(); });
      card.append(badge, title, labels, button);
      if (logos.has(corp.id)) {
        const available = document.createElement('span');
        available.className = 'logo-availability';
        available.textContent = 'Logo available';
        card.insertBefore(available, button);
      }
      cards.push(card);
    });
  }
  byId('corporation-gallery').replaceChildren(...cards);
  byId('gallery-count').textContent = `${distinctMode() ? 'Distinct' : 'Original'} colors · ${count} of ${palette.corporation_count} corporations · ${cards.length} combinations shown · ${withLogos} with logos`;
  byId('gallery-empty').hidden = count > 0;
  galleryDirty = false;
}

const panels = ['mixer', 'corporations', 'achievements'];

function setPanel(panel) {
  activePanel = panels.includes(panel) ? panel : 'mixer';
  for (const button of document.querySelectorAll('[data-panel]')) {
    const selected = button.dataset.panel === activePanel;
    button.setAttribute('aria-selected', String(selected));
    button.tabIndex = selected ? 0 : -1;
  }
  byId('mixer-panel').hidden = activePanel !== 'mixer';
  byId('corporations-panel').hidden = activePanel !== 'corporations';
  byId('achievements-panel').hidden = activePanel !== 'achievements';
  document.querySelectorAll('.mixer-choice').forEach(label => { label.hidden = activePanel !== 'mixer'; });
  history.replaceState(null, '', `#${activePanel}`);
  if (activePanel === 'corporations' && galleryDirty) renderGallery();
  if (activePanel === 'mixer') fitWideText();
  if (activePanel === 'achievements') resizeAchievementsFrame();
  updateLogoHelp();
}

function resizeAchievementsFrame() {
  const frame = byId('achievements-frame');
  try {
    const root = frame.contentDocument?.documentElement;
    if (root) frame.style.height = `${root.scrollHeight}px`;
  } catch { /* cross-origin iframe content; keep the CSS min-height fallback */ }
}

function updateWideText() {
  byId('wide-title').textContent = value('wide-title-input');
  byId('wide-subtitle').textContent = value('wide-subtitle-input');
  fitWideText();
}

function fitWideText() {
  const badge = document.querySelector('.wide-badge');
  const box = document.querySelector('.wide-text');
  const copy = document.querySelector('.wide-copy');
  if (!box.clientHeight) return;
  let scale = 1;
  for (let attempt = 0; attempt < 40; attempt++) {
    byId('wide-title').style.fontSize = `${badge.clientWidth * 0.043 * scale}px`;
    byId('wide-subtitle').style.fontSize = `${badge.clientWidth * 0.025 * scale}px`;
    if (copy.scrollHeight <= box.clientHeight && copy.scrollWidth <= box.clientWidth) break;
    scale *= 0.94;
  }
}

document.querySelectorAll('.controls select').forEach(select => select.addEventListener('change', () => {
  if (select.id === 'corporation') setCorporation(select.value);
  if (select.id === 'palette-mode') {
    const logo = value('logo');
    setCorporation(value('corporation'));
    byId('logo').value = logo;
    const url = new URL(location.href);
    if (distinctMode()) url.searchParams.delete('palette');
    else url.searchParams.set('palette', 'original');
    history.replaceState(null, '', url);
  }
  update();
}));
document.querySelectorAll('.wide-controls input').forEach(input => input.addEventListener('input', updateWideText));
byId('corporation-search').addEventListener('input', renderGallery);
byId('show-alternatives').addEventListener('change', renderGallery);
byId('logos-only').addEventListener('change', renderGallery);
byId('changed-only').addEventListener('change', () => {
  const url = new URL(location.href);
  if (byId('changed-only').checked) url.searchParams.set('changed', '1');
  else url.searchParams.delete('changed');
  history.replaceState(null, '', url);
  renderGallery();
});
byId('edit-colors').addEventListener('click', () => {
  const preset = selection();
  if (!preset) return;
  byId('metal').value = preset.variant.frame;
  byId('color').value = preset.variant.center;
  const logo = selectedLogo(preset, { ...settings(), showLogos: true });
  if (logo) byId('logo').value = logo.corporation;
  setCorporation('custom');
  update();
  byId('metal').focus();
});
document.querySelectorAll('[data-panel]').forEach(button => {
  button.addEventListener('click', () => setPanel(button.dataset.panel));
  button.addEventListener('keydown', event => {
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    let panel;
    if (event.key === 'Home') panel = panels[0];
    else if (event.key === 'End') panel = panels[panels.length - 1];
    else {
      const delta = event.key === 'ArrowRight' ? 1 : -1;
      panel = panels[(panels.indexOf(activePanel) + delta + panels.length) % panels.length];
    }
    setPanel(panel);
    document.querySelector(`[data-panel="${panel}"]`).focus();
  });
});
window.addEventListener('hashchange', () => setPanel(location.hash.slice(1)));
byId('achievements-frame').addEventListener('load', () => {
  resizeAchievementsFrame();
  try {
    const root = byId('achievements-frame').contentDocument?.documentElement;
    if (root) new ResizeObserver(resizeAchievementsFrame).observe(root);
  } catch { /* cross-origin iframe content; keep the CSS min-height fallback */ }
});
new ResizeObserver(fitWideText).observe(document.querySelector('.wide-badge'));
byId('wide-image').addEventListener('load', fitWideText);
const queryParams = new URLSearchParams(location.search);
byId('palette-mode').value = queryParams.get('palette') === 'original' ? 'original' : palette.default_palette;
byId('logos-only').checked = queryParams.get('logos') === '1';
byId('changed-only').checked = queryParams.get('changed') === '1';
setCorporation(logos.keys().next().value ?? 'custom');
updateWideText();
update();
setPanel(location.hash.slice(1));
