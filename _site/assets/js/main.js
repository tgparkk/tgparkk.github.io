// 메인 자바스크립트 파일

document.addEventListener('DOMContentLoaded', function() {
    // 테마 전환 기능 (다크모드)
    const themeSwitch = document.getElementById('theme-switch');
    if (themeSwitch) {
        const currentTheme = localStorage.getItem('theme') || 'light';
        
        if (currentTheme === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
            themeSwitch.checked = true;
        }
        
        themeSwitch.addEventListener('change', function(e) {
            if (e.target.checked) {
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
            } else {
                document.documentElement.removeAttribute('data-theme');
                localStorage.setItem('theme', 'light');
            }
        });
    }

    // 코드 블록에 복사 버튼 추가
    document.querySelectorAll('pre').forEach(function(codeBlock) {
        if (!codeBlock.querySelector('.copy-code-button')) {
            const button = document.createElement('button');
            button.className = 'copy-code-button';
            button.textContent = '복사';
            
            button.addEventListener('click', function() {
                const code = codeBlock.querySelector('code') ? 
                             codeBlock.querySelector('code').textContent : 
                             codeBlock.textContent;
                
                navigator.clipboard.writeText(code).then(function() {
                    button.textContent = '복사됨!';
                    setTimeout(function() {
                        button.textContent = '복사';
                    }, 2000);
                }, function() {
                    button.textContent = '실패!';
                });
            });
            
            codeBlock.appendChild(button);
        }
    });
});