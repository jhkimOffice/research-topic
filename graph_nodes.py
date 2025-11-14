"""
LangGraph Node Functions
각 agent를 LangGraph node로 구현
"""
import logging
from typing import Dict, Any
from graph_state import ResearchState
from agents.web_crawler_agent import WebCrawlerAgent
from agents.similarity_agent import SimilarityAgent
from agents.summarization_agent import SummarizationAgent
from agents.report_agent import ReportAgent
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def web_crawler_node(state: ResearchState) -> Dict[str, Any]:
    """
    웹 크롤링 노드
    URLs를 크롤링하고 키워드 관련 콘텐츠를 수집
    """
    logger.info("=" * 80)
    logger.info("[1/4] Web Crawler Node 실행")
    logger.info("-" * 80)

    urls = state.get('urls', [])
    query_keywords = state.get('query_keywords', [])
    config = state.get('config', {})

    # 키워드만 추출
    keywords = [kw for kw, _ in query_keywords]

    # Web Crawler Agent 초기화
    crawler = WebCrawlerAgent(
        max_depth=config.get('crawler_max_depth', 2),
        max_pages=config.get('crawler_max_pages', 50),
        delay=config.get('crawler_delay', 1.0)
    )

    # 크롤링 실행
    try:
        result = crawler.execute({
            'urls': urls,
            'keywords': keywords
        })

        if result.get('success'):
            crawled_data = result.get('data', {})
            logger.info(f"✓ 크롤링 완료: {len(crawled_data)}개 페이지 수집")

            return {
                'crawled_data': crawled_data,
                'metadata': {'crawled_pages': len(crawled_data)},
                'errors': []
            }
        else:
            error_msg = "웹 크롤링 실패"
            logger.error(error_msg)
            return {
                'crawled_data': {},
                'metadata': {'crawled_pages': 0},
                'errors': [error_msg],
                'success': False
            }

    except Exception as e:
        error_msg = f"웹 크롤링 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        import traceback
        traceback.print_exc()
        return {
            'crawled_data': {},
            'metadata': {'crawled_pages': 0},
            'errors': [error_msg],
            'success': False
        }


def similarity_node(state: ResearchState) -> Dict[str, Any]:
    """
    유사도 분석 노드
    크롤링된 콘텐츠의 유사도를 계산하고 필터링
    """
    logger.info("\n[2/4] Similarity Node 실행")
    logger.info("-" * 80)

    crawled_data = state.get('crawled_data', {})
    query_keywords = state.get('query_keywords', [])
    config = state.get('config', {})

    # 크롤링 데이터가 없으면 스킵
    if not crawled_data:
        logger.warning("크롤링된 데이터가 없습니다. 유사도 분석을 건너뜁니다.")
        return {
            'filtered_data': {},
            'metadata': {'filtered_pages': 0},
            'errors': ["크롤링된 데이터 없음"]
        }

    # Similarity Agent 초기화
    similarity_agent = SimilarityAgent(
        similarity_threshold=config.get('similarity_threshold', 0.3),
        use_transformer=config.get('use_transformer', False)
    )

    # 유사도 분석 실행
    try:
        result = similarity_agent.execute({
            'crawled_data': crawled_data,
            'query_keywords': query_keywords
        })

        if result.get('success'):
            filtered_data = result.get('filtered_data', {})
            logger.info(f"✓ 유사도 분석 완료: {len(filtered_data)}개 페이지 선택")

            return {
                'filtered_data': filtered_data,
                'metadata': {'filtered_pages': len(filtered_data)},
                'errors': []
            }
        else:
            error_msg = "유사도 분석 실패"
            logger.error(error_msg)
            return {
                'filtered_data': {},
                'metadata': {'filtered_pages': 0},
                'errors': [error_msg],
                'success': False
            }

    except Exception as e:
        error_msg = f"유사도 분석 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        import traceback
        traceback.print_exc()
        return {
            'filtered_data': {},
            'metadata': {'filtered_pages': 0},
            'errors': [error_msg],
            'success': False
        }


def summarization_node(state: ResearchState) -> Dict[str, Any]:
    """
    요약 노드
    필터링된 콘텐츠를 그룹화하고 요약
    """
    logger.info("\n[3/4] Summarization Node 실행")
    logger.info("-" * 80)

    filtered_data = state.get('filtered_data', {})
    query_keywords = state.get('query_keywords', [])
    config = state.get('config', {})

    # 필터링 데이터가 없으면 스킵
    if not filtered_data:
        logger.warning("필터링된 데이터가 없습니다. 요약을 건너뜁니다.")
        return {
            'groups': [],
            'metadata': {'total_groups': 0},
            'errors': ["필터링된 데이터 없음"]
        }

    # Summarization Agent 초기화
    summarization_agent = SummarizationAgent(
        use_llm=config.get('use_llm', False),
        use_litellm=config.get('use_litellm', True),
        litellm_model=config.get('litellm_model', None),
        api_key=config.get('openai_api_key', None)
    )

    # 요약 실행
    try:
        result = summarization_agent.execute({
            'filtered_data': filtered_data,
            'query_keywords': query_keywords
        })

        if result.get('success'):
            groups = result.get('groups', [])
            logger.info(f"✓ 요약 완료: {len(groups)}개 그룹 생성")

            return {
                'groups': groups,
                'metadata': {'total_groups': len(groups)},
                'errors': []
            }
        else:
            error_msg = "요약 실패"
            logger.error(error_msg)
            return {
                'groups': [],
                'metadata': {'total_groups': 0},
                'errors': [error_msg],
                'success': False
            }

    except Exception as e:
        error_msg = f"요약 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        import traceback
        traceback.print_exc()
        return {
            'groups': [],
            'metadata': {'total_groups': 0},
            'errors': [error_msg],
            'success': False
        }


def report_node(state: ResearchState) -> Dict[str, Any]:
    """
    보고서 생성 노드
    요약된 정보를 기반으로 마크다운 보고서 생성
    """
    logger.info("\n[4/4] Report Node 실행")
    logger.info("-" * 80)

    groups = state.get('groups', [])
    query_keywords = state.get('query_keywords', [])
    config = state.get('config', {})
    metadata = state.get('metadata', {})
    urls = state.get('urls', [])

    # Report Agent 초기화
    report_agent = ReportAgent(
        output_dir=config.get('output_dir', 'outputs')
    )

    # 메타데이터 업데이트
    full_metadata = {
        'total_urls': len(urls),
        **metadata
    }

    # 보고서 생성 실행
    try:
        result = report_agent.execute({
            'groups': groups,
            'query_keywords': query_keywords,
            'metadata': full_metadata
        })

        if result.get('success'):
            report_path = result.get('report_path', '')
            logger.info(f"✓ 보고서 생성 완료: {report_path}")

            return {
                'report_path': report_path,
                'metadata': {},
                'errors': [],
                'success': True
            }
        else:
            error_msg = "보고서 생성 실패"
            logger.error(error_msg)
            return {
                'report_path': None,
                'metadata': {},
                'errors': [error_msg],
                'success': False
            }

    except Exception as e:
        error_msg = f"보고서 생성 중 오류 발생: {str(e)}"
        logger.error(error_msg)
        import traceback
        traceback.print_exc()
        return {
            'report_path': None,
            'metadata': {},
            'errors': [error_msg],
            'success': False
        }
