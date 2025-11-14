"""
설정 파일
"""
import os
from typing import Dict, Any


class Config:
    """시스템 설정 클래스"""

    # 파일 경로
    URLS_FILE = "inputs/urls.txt"
    KEYWORDS_FILE = "inputs/keywords.txt"
    OUTPUT_DIR = "outputs"

    # Web Crawler 설정
    CRAWLER_MAX_DEPTH = 2  # 크롤링 깊이
    CRAWLER_MAX_PAGES = 2  # 최대 페이지 수
    CRAWLER_DELAY = 1.0  # 페이지 간 딜레이 (초)

    # Similarity Agent 설정
    SIMILARITY_THRESHOLD = 0.3  # 유사도 임계값 (0.0 ~ 1.0)
    USE_TRANSFORMER = False  # Transformer 모델 사용 여부 (True/False)

    # Summarization Agent 설정
    USE_LLM = True  # LLM 요약 사용 여부 (True/False)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)  # OpenAI API 키
    PREFER_LANG = 'ko'  # 요약 언어 (ko/en)

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """설정을 딕셔너리로 변환"""
        return {
            'urls_file': cls.URLS_FILE,
            'keywords_file': cls.KEYWORDS_FILE,
            'output_dir': cls.OUTPUT_DIR,
            'crawler_max_depth': cls.CRAWLER_MAX_DEPTH,
            'crawler_max_pages': cls.CRAWLER_MAX_PAGES,
            'crawler_delay': cls.CRAWLER_DELAY,
            'similarity_threshold': cls.SIMILARITY_THRESHOLD,
            'use_transformer': cls.USE_TRANSFORMER,
            'use_llm': cls.USE_LLM,
            'openai_api_key': cls.OPENAI_API_KEY,
            'prefer_lang': cls.PREFER_LANG,
        }

    @classmethod
    def print_config(cls):
        """현재 설정 출력"""
        print("\n" + "=" * 80)
        print("시스템 설정")
        print("=" * 80)
        print(f"입력 파일:")
        print(f"  - URLs: {cls.URLS_FILE}")
        print(f"  - Keywords: {cls.KEYWORDS_FILE}")
        print(f"\n크롤러 설정:")
        print(f"  - 최대 깊이: {cls.CRAWLER_MAX_DEPTH}")
        print(f"  - 최대 페이지: {cls.CRAWLER_MAX_PAGES}")
        print(f"  - 딜레이: {cls.CRAWLER_DELAY}초")
        print(f"\n유사도 설정:")
        print(f"  - 임계값: {cls.SIMILARITY_THRESHOLD}")
        print(f"  - Transformer 사용: {cls.USE_TRANSFORMER}")
        print(f"\n요약 설정:")
        print(f"  - LLM 사용: {cls.USE_LLM}")
        print(f"  - OpenAI API 키: {'설정됨' if cls.OPENAI_API_KEY else '미설정'}")
        print(f"  - 요약 언어: {cls.PREFER_LANG}")
        print(f"\n출력 디렉토리: {cls.OUTPUT_DIR}")
        print("=" * 80 + "\n")
