"""
유틸리티 함수들
"""
from typing import List, Tuple
import os


def read_urls_from_file(file_path: str) -> List[str]:
    """
    URL 파일 읽기

    Args:
        file_path: URL 파일 경로

    Returns:
        List[str]: URL 목록
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"URL 파일을 찾을 수 없습니다: {file_path}")

    urls = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 빈 줄이나 주석(#으로 시작) 무시
            if line and not line.startswith('#'):
                urls.append(line)

    return urls


def read_keywords_from_file(file_path: str) -> List[Tuple[str, str]]:
    """
    키워드 파일 읽기
    형식: keyword : description

    Args:
        file_path: 키워드 파일 경로

    Returns:
        List[Tuple[str, str]]: [(키워드, 설명), ...] 목록
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"키워드 파일을 찾을 수 없습니다: {file_path}")

    keywords = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 빈 줄이나 주석 무시
            if not line or line.startswith('#'):
                continue

            # "keyword : description" 형식 파싱
            if ':' in line:
                parts = line.split(':', 1)
                keyword = parts[0].strip()
                description = parts[1].strip() if len(parts) > 1 else ""
                keywords.append((keyword, description))
            else:
                # 콜론이 없으면 전체를 키워드로 사용
                keywords.append((line, ""))

    return keywords


def validate_inputs(urls: List[str], keywords: List[Tuple[str, str]]):
    """
    입력 데이터 유효성 검사

    Args:
        urls: URL 목록
        keywords: 키워드 목록

    Raises:
        ValueError: 입력이 유효하지 않은 경우
    """
    if not urls:
        raise ValueError("최소 1개 이상의 URL이 필요합니다.")

    if not keywords:
        raise ValueError("최소 1개 이상의 키워드가 필요합니다.")

    # URL 형식 간단 검증
    for url in urls:
        if not (url.startswith('http://') or url.startswith('https://')):
            raise ValueError(f"잘못된 URL 형식: {url}")

    print(f"✓ 입력 검증 완료: URL {len(urls)}개, 키워드 {len(keywords)}개")
