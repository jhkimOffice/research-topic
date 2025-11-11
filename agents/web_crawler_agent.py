"""
Web Crawler Agent
웹 페이지를 크롤링하고 키워드 연관 콘텐츠를 추출
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Set
import time
from agents.base_agent import BaseAgent


class WebCrawlerAgent(BaseAgent):
    """웹 크롤링 에이전트"""

    def __init__(self, max_depth: int = 2, max_pages: int = 50, delay: float = 1.0):
        super().__init__("WebCrawlerAgent")
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.delay = delay
        self.visited_urls: Set[str] = set()
        self.results: Dict[str, Dict] = {}

    def execute(self, input_data: Dict) -> Dict[str, Any]:
        """
        웹 크롤링 실행

        Args:
            input_data: {
                'urls': List[str],  # 크롤링할 URL 목록
                'keywords': List[str]  # 검색 키워드
            }

        Returns:
            Dict[str, Any]: {
                'success': bool,
                'data': Dict[str, Dict]  # {url: {'title': str, 'content': str, 'relevance': float}}
            }
        """
        urls = input_data.get('urls', [])
        keywords = input_data.get('keywords', [])

        self.log_info(f"크롤링 시작 - URLs: {len(urls)}, Keywords: {keywords}")

        for url in urls:
            self._crawl_recursive(url, keywords, depth=0)

        self.log_info(f"크롤링 완료 - 총 {len(self.results)}개 페이지 수집")

        return {
            'success': True,
            'data': self.results,
            'total_pages': len(self.results)
        }

    def _crawl_recursive(self, url: str, keywords: List[str], depth: int):
        """재귀적으로 웹 페이지 크롤링"""
        # 종료 조건
        if depth > self.max_depth or len(self.visited_urls) >= self.max_pages:
            return

        # 이미 방문한 URL이거나 유효하지 않은 URL
        if url in self.visited_urls or not self._is_valid_url(url):
            return

        self.visited_urls.add(url)
        self.log_info(f"크롤링 중 (깊이 {depth}): {url}")

        try:
            # 페이지 가져오기
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # 페이지 내용 추출
            title = self._extract_title(soup)
            content = self._extract_content(soup)

            # 키워드 관련성 체크
            relevance = self._calculate_keyword_relevance(title, content, keywords)

            if relevance > 0:
                self.results[url] = {
                    'title': title,
                    'content': content,
                    'relevance': relevance,
                    'depth': depth
                }
                self.log_info(f"관련 콘텐츠 발견 (관련도: {relevance:.2f}): {title}")

            # 하위 링크 추출 및 재귀 크롤링
            if depth < self.max_depth:
                links = self._extract_links(soup, url)
                for link in links:
                    if len(self.visited_urls) < self.max_pages:
                        time.sleep(self.delay)  # 서버 부하 방지
                        self._crawl_recursive(link, keywords, depth + 1)

        except Exception as e:
            self.log_error(f"크롤링 실패 {url}: {str(e)}")

    def _is_valid_url(self, url: str) -> bool:
        """URL 유효성 검사"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """페이지 제목 추출"""
        title = soup.find('title')
        if title:
            return title.get_text().strip()

        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()

        return "제목 없음"

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """페이지 본문 추출"""
        # 불필요한 태그 제거
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()

        # 본문 추출 시도
        content_tags = ['article', 'main', 'div[class*="content"]', 'div[class*="article"]']

        for tag_name in content_tags:
            content = soup.select_one(tag_name)
            if content:
                text = content.get_text(separator=' ', strip=True)
                if len(text) > 100:  # 충분한 내용이 있는 경우
                    return text[:5000]  # 최대 5000자

        # 기본: body 전체 텍스트
        body = soup.find('body')
        if body:
            return body.get_text(separator=' ', strip=True)[:5000]

        return ""

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """페이지에서 링크 추출"""
        links = []
        base_domain = urlparse(base_url).netloc

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(base_url, href)

            # 같은 도메인의 링크만 수집
            if urlparse(full_url).netloc == base_domain:
                links.append(full_url)

        return list(set(links))  # 중복 제거

    def _calculate_keyword_relevance(self, title: str, content: str, keywords: List[str]) -> float:
        """키워드 관련성 점수 계산"""
        if not keywords:
            return 1.0  # 키워드가 없으면 모두 관련있다고 판단

        text = (title + " " + content).lower()
        total_score = 0.0

        for keyword in keywords:
            keyword_lower = keyword.lower()
            # 제목에서 발견 시 가중치 2배
            title_count = title.lower().count(keyword_lower) * 2
            content_count = text.count(keyword_lower)
            total_score += title_count + content_count

        # 정규화
        max_possible = len(keywords) * 10
        return min(total_score / max_possible, 1.0) if max_possible > 0 else 0.0
