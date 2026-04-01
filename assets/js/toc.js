document.addEventListener('DOMContentLoaded', function () {
  var postContent = document.querySelector('.post-content');
  if (!postContent) return;

  var headings = postContent.querySelectorAll('h2, h3');
  if (headings.length < 3) return;

  var sidebar = document.querySelector('.toc-sidebar');
  var mobile = document.querySelector('.toc-mobile');
  if (sidebar) sidebar.classList.add('toc-visible');
  if (mobile) mobile.classList.add('toc-visible');

  function buildTocList() {
    var ul = document.createElement('ul');
    headings.forEach(function (h, i) {
      if (!h.id) {
        h.id = 'toc-heading-' + i;
      }
      var id = h.id;
      var li = document.createElement('li');
      li.className = 'toc-item' + (h.tagName === 'H3' ? ' toc-sub' : '');
      var a = document.createElement('a');
      a.href = '#' + id;
      a.textContent = h.textContent;
      a.setAttribute('data-toc-index', i);
      a.addEventListener('click', function (e) {
        e.preventDefault();
        h.scrollIntoView({ behavior: 'smooth', block: 'start' });
        history.replaceState(null, '', '#' + id);
      });
      li.appendChild(a);
      ul.appendChild(li);
    });
    return ul;
  }

  var desktopNav = document.getElementById('toc-desktop-nav');
  var mobileNav = document.getElementById('toc-mobile-nav');
  if (desktopNav) desktopNav.appendChild(buildTocList());
  if (mobileNav) mobileNav.appendChild(buildTocList());

  var currentActive = null;
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        var idx = Array.prototype.indexOf.call(headings, entry.target);
        if (idx === -1) return;
        if (currentActive !== null) {
          var prevLinks = document.querySelectorAll('.toc-nav a[data-toc-index="' + currentActive + '"]');
          prevLinks.forEach(function (l) { l.classList.remove('toc-active'); });
        }
        var newLinks = document.querySelectorAll('.toc-nav a[data-toc-index="' + idx + '"]');
        newLinks.forEach(function (l) { l.classList.add('toc-active'); });
        currentActive = idx;
      }
    });
  }, { rootMargin: '-80px 0px -70% 0px', threshold: 0 });

  headings.forEach(function (h) { observer.observe(h); });
});
