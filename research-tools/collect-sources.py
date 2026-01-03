#!/usr/bin/env python3
"""
돌파 전략 조사 자료 수집 도우미 스크립트
웹 페이지를 다운로드하고 정리하는 도구
"""

import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import json

# 조사할 URL 목록
SOURCES = {
    "investopedia_breakout": {
        "url": "https://www.investopedia.com/articles/trading/08/trading-breakouts.asp",
        "title": "The Anatomy of Trading Breakouts",
        "type": "online_article"
    },
    "investopedia_breakout_trader": {
        "url": "https://www.investopedia.com/terms/b/breakouttrader.asp",
        "title": "Breakout Trader: Overview, Types, and Example",
        "type": "online_article"
    },
    "axi_breakout": {
        "url": "https://www.axi.com/int/blog/education/breakout-trading-strategy",
        "title": "What is a Breakout Trading Strategy & How to Trade It?",
        "type": "online_article"
    },
    "ig_breakout": {
        "url": "https://www.ig.com/en/trading-strategies/what-is-a-breakout-trading-strategy-and-how-do-you-trade-with-it-230619",
        "title": "Breakout Trading Strategy: A Guide for Traders",
        "type": "online_article"
    }
}

def create_directories():
    """필요한 디렉토리 생성"""
    dirs = [
        "research-materials/saved-articles",
        "research-materials/saved-papers",
        "research-materials/notes"
    ]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)

def download_article(url, title, output_dir="research-materials/saved-articles"):
    """웹 페이지를 다운로드하고 저장"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # HTML 파싱
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 텍스트 추출 (본문만)
        # Investopedia의 경우 article 태그 사용
        article = soup.find('article') or soup.find('main') or soup.find('body')
        
        if article:
            text = article.get_text(separator='\n', strip=True)
        else:
            text = soup.get_text(separator='\n', strip=True)
        
        # 파일명 생성 (안전한 문자만 사용)
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_title.replace(' ', '_')}.txt"
        filepath = os.path.join(output_dir, filename)
        
        # 메타데이터와 함께 저장
        content = f"""# {title}
URL: {url}
다운로드 날짜: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

{text}
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 다운로드 완료: {filename}")
        return filepath
        
    except Exception as e:
        print(f"❌ 오류 발생 ({title}): {e}")
        return None

def save_source_list():
    """자료 목록을 JSON으로 저장"""
    output_file = "research-materials/source-list.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(SOURCES, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 자료 목록 저장: {output_file}")

def main():
    """메인 함수"""
    print("=" * 60)
    print("돌파 전략 조사 자료 수집 시작")
    print("=" * 60)
    
    # 디렉토리 생성
    create_directories()
    
    # 자료 목록 저장
    save_source_list()
    
    # 각 자료 다운로드
    print("\n📥 자료 다운로드 시작...\n")
    downloaded = []
    
    for key, source in SOURCES.items():
        print(f"\n[{key}] {source['title']}")
        filepath = download_article(source['url'], source['title'])
        if filepath:
            downloaded.append({
                "key": key,
                "title": source['title'],
                "url": source['url'],
                "filepath": filepath
            })
    
    # 다운로드 요약
    print("\n" + "=" * 60)
    print(f"✅ 총 {len(downloaded)}개 자료 다운로드 완료")
    print("=" * 60)
    
    # 다음 단계 안내
    print("\n📝 다음 단계:")
    print("1. research-materials/saved-articles/ 폴더에서 다운로드한 자료 확인")
    print("2. 각 자료를 읽고 research-notes/breakout-strategy-research.md에 정리")
    print("3. 핵심 내용과 인용구 기록")

if __name__ == "__main__":
    main()

