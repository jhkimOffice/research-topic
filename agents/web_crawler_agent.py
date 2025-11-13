"""
Web Crawler Agent
웹 페이지를 크롤링하고 키워드 연관 콘텐츠를 추출
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Set, Any
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

        # HTTP 세션 설정 (연결 재사용 및 쿠키 유지)
        self.session = requests.Session()

        # 더 현실적인 브라우저 헤더 설정
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        self.current_ua_index = 0

        self._update_headers()

    def _update_headers(self):
        """헤더 업데이트 (User-Agent 순환)"""
        self.session.headers.update({
            'User-Agent': self.user_agents[self.current_ua_index],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ko;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
        })

    def _rotate_user_agent(self):
        """User-Agent 순환"""
        self.current_ua_index = (self.current_ua_index + 1) % len(self.user_agents)
        self._update_headers()
        self.log_info(f"User-Agent 변경: {self.session.headers.get('User-Agent')[:50]}...")

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
            # 페이지 가져오기 (재시도 로직 포함)
            response = self._fetch_with_retry(url, max_retries=3)
            if response is None:
                return

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

    def _fetch_with_retry(self, url: str, max_retries: int = 3):
        """재시도 로직을 포함한 페이지 가져오기"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(
                    url,
                    timeout=15,
                    allow_redirects=True,
                    verify=True
                )
                response.raise_for_status()
                return response

            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code if e.response else None

                # 상세한 에러 정보 로깅
                if status_code is None:
                    self.log_error(f"HTTP Error without status code (시도 {attempt + 1}/{max_retries}): {url}")
                    self.log_error(f"  오류 상세: {str(e)}")
                    if attempt < max_retries - 1:
                        self._rotate_user_agent()
                        time.sleep(2 * (attempt + 1))
                        continue
                    else:
                        self.log_error(f"  접근 실패 - URL 건너뜀: {url}")
                        self.log_error(f"  대안: 이 URL은 크롤링이 제한될 수 있습니다. 다른 URL을 시도하세요.")
                        return None

                if status_code == 403:
                    self.log_warning(f"403 Forbidden (시도 {attempt + 1}/{max_retries}): {url}")
                    if attempt < max_retries - 1:
                        # 다른 User-Agent로 재시도
                        self._rotate_user_agent()
                        time.sleep(2 * (attempt + 1))  # 지수 백오프
                        continue
                    else:
                        self.log_error(f"403 Forbidden - 접근 차단된 URL 건너뜀: {url}")
                        self.log_error(f"  힌트: 이 웹사이트는 봇 크롤링을 차단합니다.")
                        self.log_error(f"  대안: robots.txt를 확인하거나, RSS 피드를 사용하거나, 다른 크롤링 가능한 URL을 시도하세요.")
                        return None

                elif status_code == 429:
                    self.log_warning(f"429 Too Many Requests - 대기 후 재시도: {url}")
                    time.sleep(5 * (attempt + 1))
                    continue

                elif status_code in [500, 502, 503, 504]:
                    self.log_warning(f"{status_code} Server Error - 재시도 {attempt + 1}/{max_retries}: {url}")
                    if attempt < max_retries - 1:
                        time.sleep(3 * (attempt + 1))
                        continue
                    else:
                        self.log_error(f"서버 오류로 인해 건너뜀: {url}")
                        return None

                else:
                    self.log_error(f"HTTP {status_code} 오류: {url}")
                    return None

            except requests.exceptions.SSLError as e:
                self.log_error(f"SSL 인증서 오류 (시도 {attempt + 1}/{max_retries}): {url}")
                self.log_error(f"  오류 상세: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    self.log_error(f"  SSL 오류로 인해 건너뜀: {url}")
                    return None

            except requests.exceptions.Timeout:
                self.log_warning(f"타임아웃 (시도 {attempt + 1}/{max_retries}): {url}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    self.log_error(f"타임아웃으로 인해 건너뜀: {url}")
                    return None

            except requests.exceptions.ConnectionError as e:
                self.log_warning(f"연결 오류 (시도 {attempt + 1}/{max_retries}): {url}")
                self.log_error(f"  오류 상세: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
                else:
                    self.log_error(f"연결 오류로 인해 건너뜀: {url}")
                    return None

            except Exception as e:
                self.log_error(f"예상치 못한 오류 (시도 {attempt + 1}/{max_retries}): {url}")
                self.log_error(f"  오류 타입: {type(e).__name__}")
                self.log_error(f"  오류 상세: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    return None

        return None

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
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'noscript']):
            tag.decompose()

        # class/id 기반 제거
        remove_keywords = [
            'ad', 'ads', 'advert', 'sponsor', 'promotion', 'ad-wrapper', 'ad-container', 'ad-banner', 'ad-box', 'ad-space', 
            'ad-unit', 'ad-slot', 'ad-placement', 'ad-placement-wrapper', 'ad-placement-container', 'ad-placement-banner', 'ad-placement-box', 'ad-placement-space', 'ad-placement-unit', # 광고 관련 태그
            'sidebar', 'related', 'recommend', 'widget', 'module', 'box' # 사이드바 관련 태그
            'popup', 'overlay', 'cookie', 'banner', # 팝업 관련 태그
            'comment', 'comments', 'reply', 'replies', # 댓글 관련 태그
            'share', 'social', 'sns', 'facebook', 'twitter', 'instagram', 'youtube', 'linkedin' # 공유 / 소셜 관련 태그
        ]

        for kw in remove_keywords:
            for tag in soup.find_all(class_=lambda x: x and kw in x.lower()): # class 기반 제거
                tag.decompose()
            for tag in soup.find_all(id=lambda x: x and kw in x.lower()): # id 기반 제거
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
