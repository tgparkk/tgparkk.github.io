(function () {
  'use strict';

  var page = document.querySelector('.archive-page');
  if (!page) return;

  var pills = page.querySelectorAll('.archive-filter-pill');
  var rows = page.querySelectorAll('.archive-row');
  var yearGroups = page.querySelectorAll('.archive-year-group');
  var jumpLinks = page.querySelectorAll('.archive-jump-link');

  var initialCategory = page.getAttribute('data-active-category') || 'all';

  function readHashCategory() {
    var match = (window.location.hash || '').match(/cat=([^&]+)/);
    return match ? decodeURIComponent(match[1]) : null;
  }

  function writeHashCategory(cat) {
    if (!cat || cat === initialCategory) {
      // Don't pollute URL when hash equals page-default category
      if (window.location.hash) {
        history.replaceState(null, '', window.location.pathname + window.location.search);
      }
      return;
    }
    history.replaceState(null, '', '#cat=' + encodeURIComponent(cat));
  }

  function applyFilter(category) {
    pills.forEach(function (pill) {
      pill.setAttribute('data-active', pill.getAttribute('data-filter') === category ? 'true' : 'false');
    });

    rows.forEach(function (row) {
      var rowCat = row.getAttribute('data-category');
      var hidden = !(category === 'all' || rowCat === category);
      if (hidden) {
        row.setAttribute('data-hidden', 'true');
      } else {
        row.removeAttribute('data-hidden');
      }
    });

    yearGroups.forEach(function (group) {
      var visible = group.querySelectorAll('.archive-row:not([data-hidden="true"])');
      if (visible.length === 0) {
        group.setAttribute('data-empty', 'true');
      } else {
        group.removeAttribute('data-empty');
      }
    });
  }

  // Pill click handlers
  pills.forEach(function (pill) {
    pill.addEventListener('click', function () {
      var cat = pill.getAttribute('data-filter');
      applyFilter(cat);
      writeHashCategory(cat);
    });
  });

  // Initial filter: hash > frontmatter category > 'all'
  var hashCat = readHashCategory();
  var startCat = hashCat || initialCategory || 'all';
  applyFilter(startCat);

  // React to hash changes (e.g., user copies a #cat=stock link)
  window.addEventListener('hashchange', function () {
    var cat = readHashCategory() || initialCategory || 'all';
    applyFilter(cat);
  });

  // Smooth scroll for year jump links
  jumpLinks.forEach(function (link) {
    link.addEventListener('click', function (e) {
      var year = link.getAttribute('data-jump-year');
      var target = document.getElementById('year-' + year);
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  // Highlight active year using IntersectionObserver
  if ('IntersectionObserver' in window && jumpLinks.length > 0) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var year = entry.target.getAttribute('data-year');
        jumpLinks.forEach(function (link) {
          link.setAttribute('data-active',
            link.getAttribute('data-jump-year') === year ? 'true' : 'false');
        });
      });
    }, { rootMargin: '-30% 0px -60% 0px', threshold: 0 });

    yearGroups.forEach(function (group) {
      observer.observe(group);
    });
  }
})();
