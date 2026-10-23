/* Local data and document navigation for the mirrored corporate website. */
(() => {
  'use strict';
  const homeData = new Map([
    ['/api/public/home-banners', '/data/home-banners.json'],
    ['/api/public/impact-reports', '/data/impact-reports.json'],
    ['/api/public/press-releases/latest', '/data/latest.json'],
  ]);
  function apiKey(url) {
    const query = new URLSearchParams(url.search);
    query.sort();
    return url.pathname + (query.size ? '?' + query.toString() : '');
  }
  function filteredCollection(url) {
    const collection = window.__COPY_COLLECTIONS__?.[url.pathname];
    if (!collection?.data?.data) return null;
    let rows = collection.data.data;
    const query = url.searchParams;
    const term = ['search', 'keyword', 'q', 'searchKeyword', 'searchText'].map(key => query.get(key)).find(Boolean)?.trim().toLocaleLowerCase();
    if (term) rows = rows.filter(row => [row.titleKo, row.contentKo, ...(row.hashtagsKo || []).map(tag => tag.name)].join(' ').toLocaleLowerCase().includes(term));
    const tags = [...query].filter(([key, value]) => /hashtag|tagId/i.test(key) && value).flatMap(([, value]) => value.split(','));
    if (tags.length) rows = rows.filter(row => (row.hashtagsKo || []).some(tag => tags.includes(String(tag.id)) || tags.includes(tag.name)));
    const page = Math.max(1, Number(query.get('page')) || 1);
    const limit = Math.max(1, Number(query.get('limit')) || 10);
    return {...collection, data: {...collection.data, data: rows.slice((page - 1) * limit, page * limit), pagination: {page, limit, total: rows.length, totalPages: Math.ceil(rows.length / limit)}}};
  }
  function dataURL(value) {
    const url = new URL(String(value), location.href);
    if (url.hostname !== 'prd-new-api.corp.musinsa.com') return value;
    const file = window.__COPY_API__?.[apiKey(url)];
    const collection = filteredCollection(url);
    if (collection) return URL.createObjectURL(new Blob([JSON.stringify(collection)], {type: 'application/json'}));
    if (file) return new URL(file, location.origin).href;
    if (homeData.has(url.pathname)) return new URL(homeData.get(url.pathname), location.origin).href;
    // Endpoints without query-dependent output (e.g. history and report data).
    const fallback = Object.entries(window.__COPY_API__ || {}).find(([key]) => key.split('?')[0] === url.pathname);
    return fallback ? new URL(fallback[1], location.origin).href : value;
  }
  const nativeOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function(method, url, ...rest) {
    const target = dataURL(url);
    if (typeof target === 'string' && target.startsWith('blob:')) this.addEventListener('loadend', () => URL.revokeObjectURL(target), {once: true});
    return nativeOpen.call(this, method, target, ...rest);
  };
  const nativeFetch = window.fetch.bind(window);
  window.fetch = function(input, options) {
    const url = typeof input === 'string' || input instanceof URL ? String(input) : input.url;
    if (new URL(url, location.href).searchParams.has('_rsc')) return Promise.resolve(new Response(null, {status: 204}));
    const target = dataURL(url);
    return nativeFetch(target === url ? input : target, options);
  };

  function destination(url) {
    const pathname = url.pathname.replace(/\/+$/, '') || '/';
    if (url.hostname === 'www.musinsacareers.com' || url.hostname === 'musinsacareers.com') {
      if (/\/o\/\d+$/.test(pathname)) return '/career/jobs/' + pathname.split('/').pop() + '/';
      if (pathname.endsWith('/benefit')) return '/career/benefit/';
      if (pathname.endsWith('/faq')) return '/career/faq/';
      return '/career/' + url.hash;
    }
    if (url.origin !== location.origin && url.hostname !== 'corp.musinsa.com') return null;
    const route = window.__COPY_ROUTES__?.[pathname];
    return route ? route + url.search + url.hash : null;
  }
  function newsroomSearch() {
    const input = document.querySelector('input[placeholder*="검색"]');
    if (!input) return;
    const url = new URL(location.href);
    url.searchParams.delete('page');
    const value = input.value.trim();
    if (value) url.searchParams.set('search', value); else url.searchParams.delete('search');
    location.assign(url.pathname + url.search);
  }
  document.addEventListener('keydown', event => {
    if (event.key === 'Enter' && event.target.matches('input[placeholder*="검색"]') && location.pathname.startsWith('/newsroom/')) {
      event.preventDefault(); event.stopImmediatePropagation(); newsroomSearch();
    }
  }, true);
  document.addEventListener('click', event => {
    if (event.button > 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    const locale = {EN: 'en', JA: 'ja', ZH: 'zh'}[event.target.textContent?.trim()];
    if (locale && event.target.closest('[class*="cursor-pointer"],button,a')) {
      event.preventDefault(); event.stopImmediatePropagation();
      const path = location.pathname.replace(/^\/ko(?=\/|$)/, '').replace(/\/$/, '');
      location.assign('https://corp.musinsa.com/' + locale + (path === '/index.html' ? '' : path)); return;
    }
    const link = event.target.closest('a');
    if (link && !link.hasAttribute('download')) {
      const target = destination(new URL(link.href, location.href));
      if (target) {
        event.preventDefault(); event.stopImmediatePropagation();
        const current = location.pathname.replace(/\/+$/, '') || '/';
        const next = new URL(target, location.origin);
        if ((next.pathname.replace(/\/+$/, '') || '/') === current && !next.search && !next.hash) {
          window.scrollTo({top: 0, behavior: 'smooth'});
        } else if (link.target === '_blank') window.open(target, '_blank', 'noopener');
        else location.assign(target);
      }
      return;
    }
    // The first Company CTA is a button using the original client's router.
    const button = event.target.closest('button');
    if (button && location.pathname.startsWith('/newsroom/') && !location.pathname.includes('/detail/')) {
      const input = document.querySelector('input[placeholder*="검색"]');
      if (input && (button.parentElement.contains(input) || button.closest('form')?.contains(input))) {
        event.preventDefault(); event.stopImmediatePropagation(); newsroomSearch(); return;
      }
      const label = button.textContent.trim();
      if (label === '전체' || label.startsWith('#')) {
        const endpoint = location.pathname.includes('/teammusinsa') ? '/api/public/team-musinsas' : '/api/public/press-releases';
        const tags = window.__COPY_COLLECTIONS__?.[endpoint]?.data?.data?.flatMap(row => row.hashtagsKo || []) || [];
        const tag = tags.find(tag => tag.name === label.slice(1));
        if (label === '전체' || tag) {
          event.preventDefault(); event.stopImmediatePropagation();
          location.assign(location.pathname + (tag ? '?hashtagId=' + tag.id : '')); return;
        }
      }
    }
    if (button && location.pathname.startsWith('/company') && /^(AI|SVG) 다운로드$/.test(button.textContent.trim())) {
      event.preventDefault(); event.stopImmediatePropagation();
      const download = document.createElement('a'); download.href = '/assets/images/common/musinsa_logo_b.svg'; download.download = 'musinsacopy.svg'; download.click(); return;
    }
    if (button && ['/', '/index.html', '/ko', '/ko/'].includes(location.pathname) && button.textContent.trim() === 'Company') {
      event.preventDefault(); event.stopImmediatePropagation();
      location.assign('/company/');
    }
  }, true);
  document.addEventListener('DOMContentLoaded', () => {
    document.documentElement.dataset.localCopy = 'true';
    if (location.hash) setTimeout(() => document.getElementById(decodeURIComponent(location.hash.slice(1)))?.scrollIntoView(), 1200);
  });
})();
