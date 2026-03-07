document.addEventListener('DOMContentLoaded', function() {
    // ===== 1. Nav Drawer 검색 (기존) =====
    var drawerSearchInput = document.querySelector('.nav-drawer .search-input');
    if (drawerSearchInput) {
      var drawerResultsContainer = document.createElement('div');
      drawerResultsContainer.id = 'search-results';
      drawerResultsContainer.className = 'search-results';
      drawerResultsContainer.style.display = 'none';
      drawerSearchInput.parentNode.appendChild(drawerResultsContainer);

      SimpleJekyllSearch({
        searchInput: drawerSearchInput,
        resultsContainer: drawerResultsContainer,
        json: '/search.json',
        searchResultTemplate: '<div class="search-item"><a href="{url}"><h4>{title}</h4></a><p>{excerpt}</p><small>{date} | {category}</small></div>',
        noResultsText: '<div class="search-no-results">검색 결과가 없습니다.</div>',
        limit: 10,
        fuzzy: false
      });

      drawerSearchInput.addEventListener('focus', function() {
        if (drawerSearchInput.value.trim() !== '') {
          drawerResultsContainer.style.display = 'block';
        }
      });

      drawerSearchInput.addEventListener('input', function() {
        drawerResultsContainer.style.display =
          drawerSearchInput.value.trim() !== '' ? 'block' : 'none';
      });

      document.addEventListener('click', function(e) {
        if (!drawerSearchInput.contains(e.target) && !drawerResultsContainer.contains(e.target)) {
          drawerResultsContainer.style.display = 'none';
        }
      });
    }

    // ===== 2. Header 검색 모달 =====
    var searchModal = document.getElementById('search-modal');
    var searchToggle = document.getElementById('header-search-toggle');
    var searchOverlay = document.getElementById('search-modal-overlay');
    var headerSearchInput = document.getElementById('header-search-input');
    var headerSearchResults = document.getElementById('header-search-results');

    if (!searchModal || !searchToggle || !headerSearchInput) return;

    // Simple-Jekyll-Search 인스턴스 생성
    SimpleJekyllSearch({
      searchInput: headerSearchInput,
      resultsContainer: headerSearchResults,
      json: '/search.json',
      searchResultTemplate: '<div class="search-item"><a href="{url}"><h4>{title}</h4></a><p>{excerpt}</p><small>{date} | {category}</small></div>',
      noResultsText: '<div class="search-no-results">검색 결과가 없습니다.</div>',
      limit: 10,
      fuzzy: false
    });

    function openSearchModal() {
      searchModal.classList.add('active');
      searchModal.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
      // 약간의 지연 후 포커스 (transition 완료 대기)
      setTimeout(function() { headerSearchInput.focus(); }, 100);
    }

    function closeSearchModal() {
      searchModal.classList.remove('active');
      searchModal.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
      headerSearchInput.value = '';
      headerSearchResults.innerHTML = '';
    }

    // 검색 버튼 클릭
    searchToggle.addEventListener('click', openSearchModal);

    // 오버레이 클릭으로 닫기
    searchOverlay.addEventListener('click', closeSearchModal);

    // ESC 키로 닫기
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && searchModal.classList.contains('active')) {
        closeSearchModal();
      }
    });

    // Ctrl+K / Cmd+K 단축키로 열기
    document.addEventListener('keydown', function(e) {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        if (searchModal.classList.contains('active')) {
          closeSearchModal();
        } else {
          openSearchModal();
        }
      }
    });
  });
