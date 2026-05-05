# Blog Content Discovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 과거 좋은 글이 묻히지 않도록, 포스트 페이지에 시리즈 배너 + 목차 사이드바를, 홈페이지에 큐레이션 패널을 추가한다.

**Architecture:** Jekyll Liquid 빌드 타임 렌더링 + 클라이언트 JS (목차 스크롤 추적, Gist 좋아요 fetch). 기존 CSS 변수 체계 활용으로 다크모드 자동 대응. 반응형 브레이크포인트: 1100px (홈 사이드바), 768px (포스트 사이드바).

**Tech Stack:** Jekyll/Liquid, Vanilla JS, CSS (기존 main.css 확장)

---

## File Structure

| Action | File | Responsibility |
|--------|------|----------------|
| Create | `_includes/series-banner.html` | 시리즈 배너 partial |
| Create | `_includes/toc-sidebar.html` | 목차 사이드바 partial |
| Create | `_includes/next-read.html` | 다음 읽을 글 카드 partial |
| Create | `_includes/curation-panel.html` | 홈 큐레이션 패널 partial |
| Create | `assets/js/toc.js` | 목차 스크롤 추적 (Intersection Observer) |
| Create | `assets/js/curation.js` | 큐레이션 탭 전환 + Gist 인기글 fetch |
| Modify | `_layouts/post.html` | 사이드바 레이아웃 + include 추가 |
| Modify | `_layouts/home.html` | 사이드바 레이아웃 + include 추가 |
| Modify | `assets/css/main.css` | 새 컴포넌트 스타일 추가 |

---

## Task 1: Series Banner

시리즈 배너 partial을 만들고 post.html에 삽입한다.

**Files:**
- Create: `_includes/series-banner.html`
- Modify: `_layouts/post.html:4-11` (post-header 앞에 배너 삽입)

- [ ] **Step 1: Create `_includes/series-banner.html`**

```html
{% if page.series %}
{% assign series_posts = site.posts | where: "series", page.series | sort: "series_order" %}
{% assign series_total = series_posts | size %}
{% if series_total > 1 %}
<div class="series-banner">
  <i class="fas fa-layer-group"></i>
  <span class="series-label">
    {{ page.series }} &mdash; <strong>{{ page.series_order }}편</strong> / 총 {{ series_total }}편
  </span>
  <div class="series-nav-links">
    {% for sp in series_posts %}
      {% if sp.url == page.url %}
        {% if forloop.index > 1 %}
          {% assign prev_index = forloop.index0 | minus: 1 %}
          <a href="{{ series_posts[prev_index].url | relative_url }}" class="series-link" title="이전: {{ series_posts[prev_index].title }}">
            <i class="fas fa-chevron-left"></i> 이전편
          </a>
        {% endif %}
        {% unless forloop.last %}
          {% assign next_index = forloop.index0 | plus: 1 %}
          <a href="{{ series_posts[next_index].url | relative_url }}" class="series-link" title="다음: {{ series_posts[next_index].title }}">
            다음편 <i class="fas fa-chevron-right"></i>
          </a>
        {% endunless %}
      {% endif %}
    {% endfor %}
  </div>
</div>
{% endif %}
{% endif %}
```

- [ ] **Step 2: Add series banner include to `_layouts/post.html`**

In `_layouts/post.html`, insert the include right after `<article class="post">` (line 5), before `<div class="post-header">`:

Find:
```html
<article class="post">
  <div class="post-header">
```

Replace with:
```html
<article class="post">
  {% include series-banner.html %}
  <div class="post-header">
```

- [ ] **Step 3: Add series banner CSS to `assets/css/main.css`**

Append to the end of `assets/css/main.css`:

```css
/* ===== Series Banner ===== */

.series-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 18px;
  margin-bottom: 24px;
  background: linear-gradient(135deg, rgba(119, 128, 235, 0.08), rgba(88, 194, 232, 0.08));
  border: 1px solid rgba(119, 128, 235, 0.2);
  border-radius: 10px;
  font-size: 0.88rem;
  color: var(--text-color);
  flex-wrap: wrap;
}

.series-banner > i {
  color: var(--accent-color);
  font-size: 1.1rem;
}

.series-banner .series-label strong {
  color: var(--accent-color);
}

.series-banner .series-nav-links {
  margin-left: auto;
  display: flex;
  gap: 12px;
}

.series-banner .series-link {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--accent-color);
  transition: var(--transition);
}

.series-banner .series-link:hover {
  color: var(--link-hover-color);
}

[data-theme="dark"] .series-banner {
  background: linear-gradient(135deg, rgba(119, 128, 235, 0.12), rgba(88, 194, 232, 0.08));
  border-color: rgba(119, 128, 235, 0.3);
}
```

- [ ] **Step 4: Test with a sample post**

Add `series` and `series_order` frontmatter to an existing post for testing:

```yaml
series: "테스트 시리즈"
series_order: 1
```

Run: `bundle exec jekyll serve`
Expected: 포스트 상단에 시리즈 배너가 보이고, 이전/다음 링크가 올바르게 동작.

- [ ] **Step 5: Commit**

```bash
git add _includes/series-banner.html _layouts/post.html assets/css/main.css
git commit -m "feat: add series banner to post pages"
```

---

## Task 2: Sticky TOC Sidebar

포스트 본문 우측에 sticky 목차 사이드바를 추가한다.

**Files:**
- Create: `_includes/toc-sidebar.html`
- Create: `assets/js/toc.js`
- Modify: `_layouts/post.html:49-52` (post-content 영역을 grid 레이아웃으로 변경)
- Modify: `assets/css/main.css` (사이드바 스타일 추가)

- [ ] **Step 1: Create `_includes/toc-sidebar.html`**

```html
<!-- Mobile TOC: collapsible toggle -->
<details class="toc-mobile">
  <summary><i class="fas fa-list"></i> 목차</summary>
  <nav id="toc-mobile-nav" class="toc-nav" aria-label="목차"></nav>
</details>

<!-- Desktop TOC: sticky sidebar -->
<aside class="toc-sidebar" aria-label="목차">
  <div class="toc-sidebar-inner">
    <h4 class="toc-sidebar-title"><i class="fas fa-list-ol"></i> 목차</h4>
    <nav id="toc-desktop-nav" class="toc-nav"></nav>
  </div>
</aside>
```

- [ ] **Step 2: Create `assets/js/toc.js`**

```javascript
document.addEventListener('DOMContentLoaded', function () {
  var postContent = document.querySelector('.post-content');
  if (!postContent) return;

  var headings = postContent.querySelectorAll('h2, h3');
  if (headings.length < 3) return; // spec: 3개 이상일 때만 표시

  // Show TOC containers
  var sidebar = document.querySelector('.toc-sidebar');
  var mobile = document.querySelector('.toc-mobile');
  if (sidebar) sidebar.style.display = 'block';
  if (mobile) mobile.style.display = 'block';

  // Build TOC list
  function buildTocList() {
    var ul = document.createElement('ul');
    headings.forEach(function (h, i) {
      var id = 'toc-heading-' + i;
      h.id = id;
      var li = document.createElement('li');
      li.className = 'toc-item' + (h.tagName === 'H3' ? ' toc-sub' : '');
      var a = document.createElement('a');
      a.href = '#' + id;
      a.textContent = h.textContent;
      a.setAttribute('data-toc-index', i);
      a.addEventListener('click', function (e) {
        e.preventDefault();
        h.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
      li.appendChild(a);
      ul.appendChild(li);
    });
    return ul;
  }

  // Insert TOC into both containers
  var desktopNav = document.getElementById('toc-desktop-nav');
  var mobileNav = document.getElementById('toc-mobile-nav');
  if (desktopNav) desktopNav.appendChild(buildTocList());
  if (mobileNav) mobileNav.appendChild(buildTocList());

  // Scroll tracking via Intersection Observer
  var currentActive = null;
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        var idx = Array.prototype.indexOf.call(headings, entry.target);
        if (idx === -1) return;
        // Remove previous active
        if (currentActive !== null) {
          var prevLinks = document.querySelectorAll('.toc-nav a[data-toc-index="' + currentActive + '"]');
          prevLinks.forEach(function (l) { l.classList.remove('toc-active'); });
        }
        // Set new active
        var newLinks = document.querySelectorAll('.toc-nav a[data-toc-index="' + idx + '"]');
        newLinks.forEach(function (l) { l.classList.add('toc-active'); });
        currentActive = idx;
      }
    });
  }, { rootMargin: '-80px 0px -70% 0px', threshold: 0 });

  headings.forEach(function (h) { observer.observe(h); });
});
```

- [ ] **Step 3: Modify `_layouts/post.html` — wrap content in grid layout**

In `_layouts/post.html`, find the existing TOC block and `post-content` div (lines 39-52):

Find:
```html
  {% if page.toc %}
  <div class="table-of-contents" data-aos="fade-up" data-aos-delay="300">
    <h2 class="toc-title">Table of Contents</h2>
    <div id="toc"></div>
  </div>
  {% endif %}

  <!-- 광고: 본문 상단 -->
  {% include ad-unit.html position="post-top" %}

  <div class="post-content" data-aos="fade-up" data-aos-delay="300">
    {{ content }}
  </div>
```

Replace with:
```html
  <!-- 광고: 본문 상단 -->
  {% include ad-unit.html position="post-top" %}

  <div class="post-body-layout">
    <div class="post-content" data-aos="fade-up" data-aos-delay="300">
      {{ content }}
    </div>
    {% include toc-sidebar.html %}
  </div>
```

- [ ] **Step 4: Add `toc.js` script to `_layouts/post.html`**

In `_layouts/post.html`, find the like-system.js script at the bottom:

Find:
```html
<!-- JavaScript for like button -->
<script src="{{ '/assets/js/like-system.js' | relative_url }}"></script>
```

Insert before it:
```html
<!-- Table of Contents -->
<script src="{{ '/assets/js/toc.js' | relative_url }}"></script>
<!-- JavaScript for like button -->
<script src="{{ '/assets/js/like-system.js' | relative_url }}"></script>
```

- [ ] **Step 5: Remove old TOC script from `_layouts/post.html`**

In the existing inline `<script>` block (around line 186+), find and remove the `generateTableOfContents` function and its call. Specifically remove:

```javascript
    // 목차 생성 함수
    function generateTableOfContents() {
      const headings = document.querySelectorAll('.post-content h2, .post-content h3');
      const toc = document.getElementById('toc');
      
      if (toc && headings.length > 0) {
        const ul = document.createElement('ul');
        
        headings.forEach((heading, index) => {
          // 앵커 ID 생성
          const id = `heading-${index}`;
          heading.id = id;
          
          const li = document.createElement('li');
          const a = document.createElement('a');
          
          a.href = `#${id}`;
          a.textContent = heading.textContent;
          
          // h3는 들여쓰기
          if (heading.tagName.toLowerCase() === 'h3') {
            li.style.marginLeft = '15px';
          }
          
          li.appendChild(a);
          ul.appendChild(li);
        });
        
        toc.appendChild(ul);
      }
    }
    
    // TOC가 활성화된 경우에만 생성
    const tocContainer = document.querySelector('.table-of-contents');
    if (tocContainer) {
      generateTableOfContents();
    }
```

- [ ] **Step 6: Add TOC sidebar CSS to `assets/css/main.css`**

Append to `assets/css/main.css`:

```css
/* ===== TOC Sidebar ===== */

.post-body-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0;
}

@media (min-width: 768px) {
  .post-body-layout {
    grid-template-columns: 1fr 240px;
    gap: 32px;
  }
}

/* Desktop sidebar */
.toc-sidebar {
  display: none; /* shown by JS when headings >= 3 */
}

@media (max-width: 767px) {
  .toc-sidebar {
    display: none !important;
  }
}

.toc-sidebar-inner {
  position: sticky;
  top: 80px;
}

.toc-sidebar-title {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--accent-color);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.toc-nav ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.toc-nav .toc-item {
  margin-bottom: 2px;
}

.toc-nav .toc-item a {
  display: block;
  padding: 5px 10px;
  font-size: 0.78rem;
  color: var(--text-light);
  border-left: 2px solid var(--border-color);
  transition: var(--transition);
  line-height: 1.4;
}

.toc-nav .toc-item a:hover {
  color: var(--accent-color);
  border-left-color: var(--accent-color);
}

.toc-nav .toc-item a.toc-active {
  color: var(--accent-color);
  border-left-color: var(--accent-color);
  font-weight: 600;
  background: rgba(119, 128, 235, 0.05);
}

.toc-nav .toc-sub a {
  padding-left: 22px;
  font-size: 0.75rem;
}

/* Mobile TOC */
.toc-mobile {
  display: none; /* shown by JS when headings >= 3 */
  margin-bottom: 20px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
}

@media (min-width: 768px) {
  .toc-mobile {
    display: none !important;
  }
}

.toc-mobile summary {
  padding: 10px 16px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--accent-color);
  cursor: pointer;
  background: rgba(119, 128, 235, 0.05);
  display: flex;
  align-items: center;
  gap: 6px;
}

.toc-mobile .toc-nav {
  padding: 8px 16px 12px;
}
```

- [ ] **Step 7: Test locally**

Run: `bundle exec jekyll serve`
- 데스크톱(768px+): 포스트 본문 우측에 sticky 목차 사이드바 확인
- 모바일(768px 미만): 접힘 토글 목차 확인
- H2/H3 3개 미만 포스트: 목차 미표시 확인
- 스크롤 시 현재 섹션 하이라이트 확인

- [ ] **Step 8: Commit**

```bash
git add _includes/toc-sidebar.html assets/js/toc.js _layouts/post.html assets/css/main.css
git commit -m "feat: add sticky TOC sidebar to post pages"
```

---

## Task 3: "Next Read" Cards

포스트 하단 Related Posts를 시리즈 이전/다음 + 크로스 카테고리 추천 카드로 교체한다.

**Files:**
- Create: `_includes/next-read.html`
- Modify: `_layouts/post.html:131-181` (기존 Related Posts 섹션 교체)
- Modify: `assets/css/main.css`

- [ ] **Step 1: Create `_includes/next-read.html`**

```html
<div class="next-read" data-aos="fade-up">
  <h2 class="section-title">Next Read</h2>
  <div class="next-read-grid">

    {% comment %} Left card: series prev/next or same-category prev/next {% endcomment %}
    {% if page.series %}
      {% assign series_posts = site.posts | where: "series", page.series | sort: "series_order" %}
      {% assign current_order = page.series_order %}
      {% assign prev_post = nil %}
      {% assign next_post = nil %}
      {% for sp in series_posts %}
        {% if sp.series_order < current_order %}
          {% assign prev_post = sp %}
        {% endif %}
        {% if sp.series_order > current_order and next_post == nil %}
          {% assign next_post = sp %}
        {% endif %}
      {% endfor %}
    {% else %}
      {% assign cat = page.categories | first %}
      {% assign cat_posts = site.posts | where_exp: "p", "p.categories contains cat" | sort: "date" %}
      {% assign prev_post = nil %}
      {% assign next_post = nil %}
      {% assign found_current = false %}
      {% for cp in cat_posts %}
        {% if cp.url == page.url %}
          {% assign found_current = true %}
        {% elsif found_current == false %}
          {% assign prev_post = cp %}
        {% elsif next_post == nil %}
          {% assign next_post = cp %}
        {% endif %}
      {% endfor %}
    {% endif %}

    <div class="next-read-card">
      {% if prev_post %}
        <div class="next-read-label"><i class="fas fa-arrow-left"></i>
          {% if page.series %}이전 편{% else %}이전 글{% endif %}
        </div>
        <h4><a href="{{ prev_post.url | relative_url }}">{{ prev_post.title }}</a></h4>
        <div class="next-read-meta">
          {% if page.series %}{{ prev_post.series_order }}편 &middot; {% endif %}
          {{ prev_post.date | date: "%Y-%m-%d" }}
        </div>
      {% else %}
        <div class="next-read-label"><i class="fas fa-arrow-left"></i>
          {% if page.series %}첫 번째 편입니다{% else %}이전 글 없음{% endif %}
        </div>
        <div class="next-read-empty">시리즈의 시작이에요!</div>
      {% endif %}
    </div>

    {% comment %} Right card: cross-category recommendation by tags {% endcomment %}
    <div class="next-read-card">
      {% assign recommended = nil %}
      {% for post in site.posts %}
        {% if post.url != page.url and recommended == nil %}
          {% assign same_category = false %}
          {% for cat in post.categories %}
            {% if page.categories contains cat %}
              {% assign same_category = true %}
            {% endif %}
          {% endfor %}
          {% if same_category == false %}
            {% for tag in post.tags %}
              {% if page.tags contains tag and recommended == nil %}
                {% assign recommended = post %}
              {% endif %}
            {% endfor %}
          {% endif %}
        {% endif %}
      {% endfor %}

      {% if recommended %}
        <div class="next-read-label">
          다른 주제 추천 <i class="fas fa-random"></i>
        </div>
        <h4><a href="{{ recommended.url | relative_url }}">{{ recommended.title }}</a></h4>
        <div class="next-read-meta">
          {{ recommended.categories | first }} &middot; {{ recommended.date | date: "%Y-%m-%d" }}
        </div>
      {% elsif next_post %}
        <div class="next-read-label">
          {% if page.series %}다음 편{% else %}다음 글{% endif %} <i class="fas fa-arrow-right"></i>
        </div>
        <h4><a href="{{ next_post.url | relative_url }}">{{ next_post.title }}</a></h4>
        <div class="next-read-meta">
          {% if page.series %}{{ next_post.series_order }}편 &middot; {% endif %}
          {{ next_post.date | date: "%Y-%m-%d" }}
        </div>
      {% else %}
        <div class="next-read-label">추천 글 <i class="fas fa-star"></i></div>
        <div class="next-read-empty">더 많은 글이 곧 올라옵니다!</div>
      {% endif %}
    </div>

  </div>
</div>
```

- [ ] **Step 2: Replace Related Posts in `_layouts/post.html`**

Find the entire related posts block (lines 131-181):

```html
  <!-- 관련 게시물 -->
  <div class="related-posts" data-aos="fade-up">
    <h2 class="section-title">Related Posts</h2>
    <div class="post-grid">
      {% assign maxRelated = 3 %}
```

...through to the closing `</div>` of `.related-posts`:

```html
    </div>
  </div>
```

Replace the entire block with:

```html
  {% include next-read.html %}
```

- [ ] **Step 3: Add Next Read CSS to `assets/css/main.css`**

Append to `assets/css/main.css`:

```css
/* ===== Next Read Cards ===== */

.next-read {
  margin-top: 40px;
  padding-top: 30px;
  border-top: 1px solid var(--border-color);
}

.next-read-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

@media (max-width: 600px) {
  .next-read-grid {
    grid-template-columns: 1fr;
  }
}

.next-read-card {
  padding: 20px;
  border-radius: 10px;
  border: 1px solid var(--border-color);
  background: var(--card-bg);
  transition: var(--transition);
}

.next-read-card:hover {
  box-shadow: var(--card-shadow);
  transform: translateY(-2px);
}

.next-read-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--accent-color);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.next-read-card h4 {
  font-size: 0.92rem;
  margin-bottom: 6px;
  line-height: 1.4;
}

.next-read-card h4 a {
  color: var(--heading-color);
}

.next-read-card h4 a:hover {
  color: var(--accent-color);
}

.next-read-meta {
  font-size: 0.75rem;
  color: var(--text-light);
}

.next-read-empty {
  font-size: 0.85rem;
  color: var(--text-light);
  padding: 10px 0;
}
```

- [ ] **Step 4: Test locally**

Run: `bundle exec jekyll serve`
- 시리즈 포스트: 이전/다음 편 카드 확인
- 일반 포스트: 같은 카테고리 이전/다음 + 크로스 카테고리 추천 확인
- 모바일: 1열 레이아웃으로 전환 확인

- [ ] **Step 5: Commit**

```bash
git add _includes/next-read.html _layouts/post.html assets/css/main.css
git commit -m "feat: replace related posts with next-read cards"
```

---

## Task 4: Homepage Curation Panel

홈 우측에 인기글/시리즈/주제별 3탭 큐레이션 패널을 추가한다.

**Files:**
- Create: `_includes/curation-panel.html`
- Create: `assets/js/curation.js`
- Modify: `_layouts/home.html:66-111` (Recent Posts 영역을 grid 레이아웃으로 래핑)
- Modify: `assets/css/main.css`

- [ ] **Step 1: Create `assets/js/curation.js`**

```javascript
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

      // Build post map from DOM data attributes
      var postDataEls = document.querySelectorAll('.curation-post-data');
      var postMap = {};
      postDataEls.forEach(function (el) {
        postMap[el.getAttribute('data-id')] = {
          title: el.getAttribute('data-title'),
          url: el.getAttribute('data-url'),
          category: el.getAttribute('data-category')
        };
      });

      // Sort by likes descending
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
```

- [ ] **Step 2: Create `_includes/curation-panel.html`**

```html
<!-- Hidden post data for JS popularity ranking -->
{% for post in site.posts %}
<span class="curation-post-data" hidden
  data-id="{{ post.url | slugify }}"
  data-title="{{ post.title | escape }}"
  data-url="{{ post.url | relative_url }}"
  data-category="{{ post.categories | first }}"></span>
{% endfor %}

<div class="curation-panel">
  <div class="curation-tabs">
    <button class="curation-tab-btn active" data-tab="popular">
      <i class="fas fa-fire"></i> 인기글
    </button>
    <button class="curation-tab-btn" data-tab="series">
      <i class="fas fa-layer-group"></i> 시리즈
    </button>
    <button class="curation-tab-btn" data-tab="topics">
      <i class="fas fa-folder"></i> 주제별
    </button>
  </div>

  <!-- Popular Tab -->
  <div id="curation-popular" class="curation-tab-panel" style="display: block;">
    <div id="curation-popular-list">
      <div class="curation-skeleton">
        <div class="skeleton-line"></div>
        <div class="skeleton-line short"></div>
        <div class="skeleton-line"></div>
        <div class="skeleton-line short"></div>
        <div class="skeleton-line"></div>
      </div>
    </div>
  </div>

  <!-- Series Tab -->
  <div id="curation-series" class="curation-tab-panel" style="display: none;">
    {% assign all_series = "" %}
    {% for post in site.posts %}
      {% if post.series %}
        {% unless all_series contains post.series %}
          {% if all_series != "" %}{% assign all_series = all_series | append: "|||" %}{% endunless %}
          {% assign all_series = all_series | append: post.series %}
        {% endunless %}
      {% endif %}
    {% endfor %}

    {% assign series_list = all_series | split: "|||" %}
    {% for series_name in series_list %}
      {% assign s_posts = site.posts | where: "series", series_name | sort: "series_order" %}
      {% assign s_count = s_posts | size %}
      {% if s_count > 1 %}
      <div class="curation-series-item">
        <h5>{{ series_name }}</h5>
        <div class="curation-series-meta">
          <span><i class="fas fa-layer-group"></i> {{ s_count }}편</span>
        </div>
        <a href="{{ s_posts.first.url | relative_url }}" class="curation-series-start">
          1편부터 시작하기 <i class="fas fa-arrow-right"></i>
        </a>
      </div>
      {% endif %}
    {% endfor %}

    {% if series_list.size == 0 %}
      <div class="curation-empty">아직 시리즈가 없습니다.</div>
    {% endif %}
  </div>

  <!-- Topics Tab -->
  <div id="curation-topics" class="curation-tab-panel" style="display: none;">
    {% assign categories_sorted = "cpp,async_servers,gamedev,rendering,windows,security,stock,robotrader,trading-journal,machine-learning,hobby,cooking,book,english,review,blog-analysis" | split: "," %}
    {% assign cat_icons = "fa-code,fa-server,fa-gamepad,fa-paint-brush,fab fa-windows,fa-shield-alt,fa-chart-line,fa-robot,fa-journal-whills,fa-brain,fa-puzzle-piece,fa-utensils,fa-book,fa-language,fa-star,fa-chart-bar" | split: "," %}
    {% for cat in categories_sorted %}
      {% assign cat_posts = site.posts | where_exp: "p", "p.categories contains cat" %}
      {% assign cat_count = cat_posts | size %}
      {% if cat_count > 0 %}
      <a href="{{ '/categories/' | append: cat | relative_url }}/" class="curation-topic-item">
        <span class="curation-topic-icon"><i class="fas {{ cat_icons[forloop.index0] }}"></i></span>
        <span class="curation-topic-name">{{ cat }}</span>
        <span class="curation-topic-count">{{ cat_count }}편</span>
      </a>
      {% endif %}
    {% endfor %}
  </div>
</div>
```

- [ ] **Step 3: Modify `_layouts/home.html` — wrap in grid layout**

Find in `home.html` the recent posts section (line 67):

```html
<!-- 최근 게시물 -->
<section class="recent-posts-section">
```

Replace from `<!-- 최근 게시물 -->` through the closing `</section>` (line 111) with:

```html
<!-- 최근 게시물 + 큐레이션 패널 -->
<section class="recent-posts-section">
  <div class="home-content-layout">
    <div class="home-main-col">
      <div class="section-title-container" data-aos="fade-up" data-aos-duration="800">
        <h2 class="section-title">Recent Posts</h2>
        <a href="{{ '/categories/all/' | relative_url }}" class="view-all">View All <i class="fas fa-arrow-right"></i></a>
      </div>

      <div class="post-grid">
        {% for post in site.posts limit:6 %}
          <div class="post-card" data-aos="fade-up" data-aos-duration="800" data-aos-delay="{{ forloop.index | times: 100 }}">
            {% if post.image %}
              <div class="post-card-image-container">
                <img src="{{ post.image | relative_url }}" alt="{{ post.title }}" class="post-card-image">
              </div>
            {% else %}
              <div class="post-card-image-container default-image">
                <i class="fas fa-file-alt default-icon"></i>
              </div>
            {% endif %}
            
            <div class="post-card-content">
              <div class="post-card-meta">
                <span class="post-date"><i class="far fa-calendar-alt"></i> {{ post.date | date: "%Y-%m-%d" }}</span>
                {% if post.categories.size > 0 %}
                <span class="post-category">
                  {% for category in post.categories limit:1 %}
                    <a href="{{ '/categories/' | append: category | relative_url }}/">{{ category }}</a>
                  {% endfor %}
                </span>
                {% endif %}
              </div>
              
              <h3><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
              
              {% if post.excerpt %}
                <div class="post-excerpt">
                  {{ post.excerpt | strip_html | truncatewords: 20 }}
                </div>
              {% endif %}
              
              <a href="{{ post.url | relative_url }}" class="read-more">Read More</a>
            </div>
          </div>
        {% endfor %}
      </div>
    </div>

    <div class="home-curation-col">
      {% include curation-panel.html %}
    </div>
  </div>

  <!-- Mobile: curation below grid -->
  <div class="home-curation-mobile">
    {% include curation-panel.html %}
  </div>
</section>
```

- [ ] **Step 4: Add `curation.js` script to `_layouts/home.html`**

At the bottom of `home.html`, before the closing `</script>` or after it, add:

```html
<script src="{{ '/assets/js/curation.js' | relative_url }}"></script>
```

- [ ] **Step 5: Add Curation Panel CSS to `assets/css/main.css`**

Append to `assets/css/main.css`:

```css
/* ===== Homepage Content Layout ===== */

.home-content-layout {
  display: grid;
  grid-template-columns: 1fr;
}

.home-curation-col {
  display: none;
}

.home-curation-mobile {
  display: block;
  margin-top: 40px;
}

@media (min-width: 1100px) {
  .home-content-layout {
    grid-template-columns: 1fr 300px;
    gap: 32px;
  }
  .home-curation-col {
    display: block;
  }
  .home-curation-mobile {
    display: none;
  }
}

/* ===== Curation Panel ===== */

.curation-panel {
  position: sticky;
  top: 80px;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}

.curation-tabs {
  display: flex;
  background: var(--primary-color);
}

.curation-tab-btn {
  flex: 1;
  padding: 11px 8px;
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.5);
  font-family: inherit;
  font-size: 0.72rem;
  font-weight: 600;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: var(--transition);
}

.curation-tab-btn:hover {
  color: rgba(255, 255, 255, 0.8);
}

.curation-tab-btn.active {
  color: #fff;
  border-bottom-color: var(--accent-color);
}

.curation-tab-panel {
  padding: 14px;
}

/* Popular items */
.curation-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-color);
}

.curation-item:last-child {
  border-bottom: none;
}

.curation-rank {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  background: var(--accent-color);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: 700;
  flex-shrink: 0;
}

.curation-rank.silver {
  background: var(--text-light);
}

.curation-info {
  min-width: 0;
}

.curation-title {
  display: block;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--heading-color);
  margin-bottom: 3px;
  line-height: 1.35;
}

.curation-title:hover {
  color: var(--accent-color);
}

.curation-stats {
  font-size: 0.7rem;
  color: var(--text-light);
  display: flex;
  gap: 10px;
}

.curation-stats i {
  color: var(--accent-color);
}

/* Skeleton loading */
.curation-skeleton {
  padding: 4px 0;
}

.skeleton-line {
  height: 12px;
  background: var(--border-color);
  border-radius: 4px;
  margin-bottom: 14px;
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-line.short {
  width: 60%;
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 1; }
}

/* Series items */
.curation-series-item {
  padding: 12px;
  background: rgba(119, 128, 235, 0.04);
  border-radius: 8px;
  border: 1px solid var(--border-color);
  margin-bottom: 10px;
}

.curation-series-item h5 {
  font-size: 0.82rem;
  color: var(--heading-color);
  margin-bottom: 4px;
}

.curation-series-meta {
  font-size: 0.72rem;
  color: var(--text-light);
  display: flex;
  gap: 10px;
}

.curation-series-meta i {
  color: var(--accent-color);
}

.curation-series-start {
  display: inline-block;
  margin-top: 8px;
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--accent-color);
}

.curation-series-start:hover {
  color: var(--link-hover-color);
}

/* Topic items */
.curation-topic-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 4px;
  border-bottom: 1px solid var(--border-color);
  color: var(--heading-color);
  transition: var(--transition);
}

.curation-topic-item:last-child {
  border-bottom: none;
}

.curation-topic-item:hover {
  color: var(--accent-color);
}

.curation-topic-icon {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background: var(--accent-color);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 0.72rem;
  flex-shrink: 0;
}

.curation-topic-name {
  flex: 1;
  font-size: 0.82rem;
  font-weight: 600;
}

.curation-topic-count {
  font-size: 0.72rem;
  color: var(--text-light);
}

.curation-empty {
  text-align: center;
  padding: 20px 0;
  font-size: 0.82rem;
  color: var(--text-light);
}
```

- [ ] **Step 6: Test locally**

Run: `bundle exec jekyll serve`
- 데스크톱(1100px+): 홈 우측에 큐레이션 패널, 탭 전환 동작 확인
- 모바일(1100px 미만): 포스트 그리드 아래에 패널 전체폭 표시 확인
- 인기글 탭: Gist 데이터 로딩 → 순위 표시 확인
- 시리즈 탭: series frontmatter가 있는 포스트 그룹 확인
- 주제별 탭: 카테고리 목록 + 글 수 확인
- 다크모드 전환 시 스타일 확인

- [ ] **Step 7: Commit**

```bash
git add _includes/curation-panel.html assets/js/curation.js _layouts/home.html assets/css/main.css
git commit -m "feat: add curation panel to homepage"
```

---

## Task 5: Cleanup & Polish

목업 파일 정리, 테스트 시리즈 frontmatter 제거, 전체 동작 확인.

- [ ] **Step 1: Remove mockup directory**

```bash
rm -rf _mockups/
```

- [ ] **Step 2: Remove test series frontmatter**

Task 1에서 테스트용으로 추가한 `series`/`series_order` frontmatter가 실제 시리즈가 아닌 포스트에 남아있다면 제거.

- [ ] **Step 3: Full integration test**

Run: `bundle exec jekyll serve`

체크리스트:
- [ ] 홈 히어로, 카테고리 아이콘 정상 (기존 기능 유지)
- [ ] 홈 큐레이션 패널 3탭 전환 동작
- [ ] 홈 모바일 레이아웃 확인
- [ ] 포스트 시리즈 배너 표시 (series 있는 글)
- [ ] 포스트 시리즈 배너 미표시 (series 없는 글)
- [ ] 포스트 목차 사이드바 (heading 3개 이상)
- [ ] 포스트 목차 스크롤 추적 하이라이트
- [ ] 포스트 모바일 목차 토글
- [ ] 포스트 하단 Next Read 카드
- [ ] 다크모드 전체 컴포넌트 확인
- [ ] 검색 모달 (Ctrl+K) 정상 동작

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "chore: cleanup mockups and finalize content discovery redesign"
```
