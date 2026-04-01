document.addEventListener('DOMContentLoaded', function () {
  // Tab switching
  var tabs = document.querySelectorAll('.curation-tab-btn');
  var panels = document.querySelectorAll('.curation-tab-panel');

  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      var target = this.getAttribute('data-tab');
      tabs.forEach(function (t) { t.classList.remove('active'); });
      panels.forEach(function (p) { p.style.display = 'none'; });
      this.classList.add('active');
      var panel = document.getElementById('curation-' + target);
      if (panel) panel.style.display = 'block';
    });
  });

  // Fetch popular posts from Gist likes
  fetchPopularPosts();

  async function fetchPopularPosts() {
    var container = document.getElementById('curation-popular-list');
    if (!container) return;

    try {
      var response = await fetch('/api/likes.html?action=get');
      var text = await response.text();
      var jsonStart = text.indexOf('{');
      var jsonEnd = text.lastIndexOf('}') + 1;
      if (jsonStart === -1 || jsonEnd === 0) throw new Error('Invalid format');
      var data = JSON.parse(text.substring(jsonStart, jsonEnd));
      var likes = data.likes || {};

      var postDataEls = document.querySelectorAll('.curation-post-data');
      var postMap = {};
      postDataEls.forEach(function (el) {
        postMap[el.getAttribute('data-id')] = {
          title: el.getAttribute('data-title'),
          url: el.getAttribute('data-url'),
          category: el.getAttribute('data-category')
        };
      });

      var sorted = Object.keys(likes)
        .filter(function (id) { return postMap[id]; })
        .sort(function (a, b) { return (likes[b] || 0) - (likes[a] || 0); })
        .slice(0, 5);

      if (sorted.length === 0) {
        container.innerHTML = '<div class="curation-empty">아직 좋아요 데이터가 없습니다.</div>';
        return;
      }

      var html = '';
      sorted.forEach(function (id, i) {
        var post = postMap[id];
        var count = likes[id] || 0;
        html += '<div class="curation-item">'
          + '<div class="curation-rank' + (i >= 3 ? ' silver' : '') + '">' + (i + 1) + '</div>'
          + '<div class="curation-info">'
          + '<a href="' + post.url + '" class="curation-title">' + post.title + '</a>'
          + '<div class="curation-stats">'
          + '<span><i class="fas fa-heart"></i> ' + count + '</span>'
          + '<span>' + post.category + '</span>'
          + '</div></div></div>';
      });
      container.innerHTML = html;
    } catch (e) {
      console.error('Curation popular fetch error:', e);
      container.innerHTML = '<div class="curation-empty">인기글을 불러오는 중...</div>';
    }
  }
});
