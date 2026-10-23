/* Local interactions for the preserved recruiting pages. */
(() => {
  'use strict';
  const jobs = [...document.querySelectorAll('[data-testid="공고_아이템"]')];
  let overlay;
  let popover;
  const state = new Map();
  const known = {'회사 홈페이지':'/','복리후생':'/career/benefit/','FAQ':'/career/faq/','채용 중인 공고':'/career/#f9221335-0b3f-4011-b3ac-1ed1a0e34984'};
  function filterJobs() {
    let count = 0;
    jobs.forEach(job => {
      const visible = [...state].every(([group, values]) => !values.size || [...values].some(value => {
        const meta = job.querySelector('[data-testid="공고리스트_subtext_' + group + '"]');
        const text = meta?.textContent.trim() || job.textContent;
        return meta ? text === value : text.includes(value);
      }));
      job.hidden = !visible;
      if (visible) count++;
    });
    if (jobs.length) {
      let empty = document.getElementById('career-empty');
      if (!empty) { empty = document.createElement('p'); empty.id = 'career-empty'; empty.className = 'career-empty'; empty.textContent = '선택한 조건에 맞는 공고가 없습니다.'; jobs[0].parentElement.append(empty); }
      empty.hidden = count !== 0;
    }
  }
  document.addEventListener('change', event => {
    const input = event.target;
    if (!input.matches('input[type="checkbox"][id]')) return;
    const [group, value] = input.id.split('_');
    if (!group || !value) return;
    if (!state.has(group)) state.set(group, new Set());
    if (input.checked) state.get(group).add(value); else state.get(group).delete(value);
    document.querySelectorAll('input[type="checkbox"]').forEach(other => { if (other.id === input.id) other.checked = input.checked; });
    filterJobs();
  });
  function closeOverlay() { overlay?.remove(); overlay = null; document.body.style.overflow = ''; }
  function openOverlay(content) {
    closeOverlay(); overlay = document.createElement('div'); overlay.className = 'career-overlay'; overlay.setAttribute('role','dialog'); overlay.setAttribute('aria-modal','true');
    const close = document.createElement('button'); close.textContent = '×'; close.setAttribute('aria-label','닫기'); close.addEventListener('click', closeOverlay);
    overlay.append(close, content); document.body.append(overlay); document.body.style.overflow = 'hidden'; close.focus();
  }
  function mobileMenu() {
    const nav = document.createElement('nav');
    for (const [label, href] of Object.entries(known)) { const a = document.createElement('a'); a.textContent = label; a.href = href; a.addEventListener('click',closeOverlay); nav.append(a); }
    openOverlay(nav);
  }
  let menuConfig;
  const configuration = fetch('/data/career-menu.json').then(r => r.json()).then(value => {menuConfig = value; return value;});
  function showSubmenu(button) {
    configuration.then(() => {
      popover?.remove();
      const menu = menuConfig.design.header.menus.find(item => item.id === button.id);
      if (!menu?.subMenus?.length) return;
      popover = document.createElement('div'); popover.className = 'career-popover';
      menu.subMenus.forEach(item => {
        const a = document.createElement('a');
        const page = menuConfig.design.pages.find(page => page.id === item.link.pageId);
        a.textContent = item.link.name || page?.name || '팀 소개';
        a.href = item.link.url || (page ? '/career/' + page.path + '/' : '/newsroom/teammusinsa/');
        if (a.href.includes('newsroom.musinsa.com')) a.href = '/newsroom/press/';
        if (item.link.isNewTab) {a.target = '_blank'; a.rel = 'noopener';}
        popover.append(a);
      });
      const rect = button.getBoundingClientRect(); popover.style.left = rect.left + scrollX + 'px'; popover.style.top = rect.bottom + scrollY + 4 + 'px'; document.body.append(popover);
    });
  }
  document.addEventListener('click', event => {
    const title = event.target.closest('[class*="toggle__ToggleBlockTitleContainer"]');
    if (title) {const body = title.nextElementSibling; if (body) { const expanded = body.style.height !== '0px' && body.style.height !== '0'; body.style.height = expanded ? '0px' : body.scrollHeight + 'px'; title.setAttribute('aria-expanded',String(!expanded)); } return;}
    const collapse = event.target.closest('[class*="collapse__Header"]');
    if (collapse) {const body = collapse.nextElementSibling; if (body) {const closed = body.style.height === '0px'; body.style.height = closed ? 'auto' : '0px';body.style.overflow = 'hidden';}return;}
    const button = event.target.closest('button');
    if (button?.getAttribute('data-testid') === '모바일_메뉴_버튼') {mobileMenu();return;}
    if (button && known[button.name]) {location.assign(known[button.name]);return;}
    if (button?.name && !known[button.name]) {showSubmenu(button);return;}
    if (button?.textContent.trim() === '필터') {const filters = document.querySelector('[class*="block-filters__Container"]'); if (filters) openOverlay(filters.cloneNode(true));return;}
    if (button && /지원하기|지원서 작성/.test(button.textContent)) {
      event.preventDefault(); event.stopImmediatePropagation();
      const id = location.pathname.match(/\/jobs\/(\d+)/)?.[1];
      if (id) window.open('https://www.musinsacareers.com/ko/o/' + id + '/apply', '_blank', 'noopener');
      return;
    }
    if (!event.target.closest('.career-popover')) popover?.remove();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') {closeOverlay();popover?.remove();}
    if ((event.key === 'Enter' || event.key === ' ') && event.target.matches('[class*="toggle__ToggleBlockTitleContainer"]')) {event.preventDefault();event.target.click();}
  });
  document.querySelectorAll('[class*="toggle__ToggleBlockTitleContainer"]').forEach(title => {title.tabIndex = 0;title.setAttribute('role','button');title.setAttribute('aria-expanded','false');});
  document.querySelectorAll('a[target="_blank"]').forEach(a => a.rel = 'noopener noreferrer');
})();
