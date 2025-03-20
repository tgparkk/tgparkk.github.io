document.addEventListener('DOMContentLoaded', function() {
    // 검색 입력창과 결과 컨테이너 요소 가져오기
    const searchInput = document.querySelector('.search-input');
    
    // 검색 결과를 표시할 컨테이너 생성 및 스타일 설정
    const searchResultsContainer = document.createElement('div');
    searchResultsContainer.id = 'search-results';
    searchResultsContainer.className = 'search-results';
    searchResultsContainer.style.display = 'none';
    
    // 검색 입력창 아래에 결과 컨테이너 추가
    searchInput.parentNode.appendChild(searchResultsContainer);
    
    // Simple-Jekyll-Search 설정
    const sjs = SimpleJekyllSearch({
      searchInput: searchInput,
      resultsContainer: searchResultsContainer,
      json: '/search.json',
      searchResultTemplate: '<div class="search-item"><a href="{url}"><h4>{title}</h4></a><p>{excerpt}</p><small>{date} | {category}</small></div>',
      noResultsText: '검색 결과가 없습니다.',
      limit: 10,
      fuzzy: false
    });
    
    // 검색창에 포커스가 있을 때 결과 표시
    searchInput.addEventListener('focus', function() {
      if (searchInput.value.trim() !== '') {
        searchResultsContainer.style.display = 'block';
      }
    });
    
    // 검색창에 입력이 있을 때 결과 표시
    searchInput.addEventListener('input', function() {
      if (searchInput.value.trim() !== '') {
        searchResultsContainer.style.display = 'block';
      } else {
        searchResultsContainer.style.display = 'none';
      }
    });
    
    // 문서의 다른 곳을 클릭하면 결과 닫기
    document.addEventListener('click', function(e) {
      if (!searchInput.contains(e.target) && !searchResultsContainer.contains(e.target)) {
        searchResultsContainer.style.display = 'none';
      }
    });
  });