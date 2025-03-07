// GitHub Actions를 사용한 좋아요 시스템 (토큰 노출 없음)
document.addEventListener('DOMContentLoaded', function() {
    // API 엔드포인트 (GitHub Pages에 배포됨)
    const API_ENDPOINT = '/api/likes.html';
    
    const likeButton = document.getElementById('like-button');
    if (!likeButton) return; // 좋아요 버튼이 없으면 실행 중지
    
    const likeCount = document.getElementById('like-count');
    const postId = likeButton.getAttribute('data-post-id');
    
    // localStorage에서 좋아요 상태 확인
    const likedPosts = JSON.parse(localStorage.getItem('likedPosts') || '{}');
    
    // 이미 좋아요를 눌렀는지 확인하고 UI 업데이트
    if (likedPosts[postId]) {
      likeButton.classList.add('liked');
    }
    
    // Gist에서 좋아요 데이터 가져오기
    fetchLikes();
    
    // 좋아요 버튼 클릭 이벤트
    likeButton.addEventListener('click', function() {
      if (!likedPosts[postId]) {
        // 좋아요 추가
        likedPosts[postId] = true;
        localStorage.setItem('likedPosts', JSON.stringify(likedPosts));
        likeButton.classList.add('liked');
        updateLikes(1);
      } else {
        // 좋아요 취소
        delete likedPosts[postId];
        localStorage.setItem('likedPosts', JSON.stringify(likedPosts));
        likeButton.classList.remove('liked');
        updateLikes(-1);
      }
    });
    
    // 좋아요 데이터 가져오기
    async function fetchLikes() {
      try {
        const response = await fetch(`${API_ENDPOINT}?action=get`);
        const text = await response.text();
        
        // HTML에서 JSON 추출 (API는 HTML 페이지를 반환)
        const jsonStart = text.indexOf('{');
        const jsonEnd = text.lastIndexOf('}') + 1;
        const jsonStr = text.substring(jsonStart, jsonEnd);
        
        if (jsonStart === -1 || jsonEnd === 0) {
          throw new Error('Invalid response format');
        }
        
        const data = JSON.parse(jsonStr);
        
        // 이 포스트의 좋아요 수 표시
        const likes = data.likes[postId] || 0;
        likeCount.textContent = likes;
        
      } catch (error) {
        console.error('좋아요 데이터를 가져오는데 오류 발생:', error);
      }
    }
    
    // 좋아요 업데이트
    async function updateLikes(change) {
      try {
        // 옵티미스틱 UI 업데이트 (API 응답 전에 UI 먼저 변경)
        const currentCount = parseInt(likeCount.textContent) || 0;
        likeCount.textContent = Math.max(0, currentCount + change);
        
        // API 호출
        await fetch(`${API_ENDPOINT}?action=update&postId=${encodeURIComponent(postId)}&change=${change}`);
        
        // 실제 업데이트 확인을 위해 잠시 후 좋아요 수를 다시 가져오기
        setTimeout(fetchLikes, 5000);
        
      } catch (error) {
        console.error('좋아요 업데이트 중 오류 발생:', error);
        // 오류 발생시 UI 롤백
        fetchLikes();
      }
    }
  });