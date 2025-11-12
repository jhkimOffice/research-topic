"""
LangGraph Workflow
Multi-Agent Research System의 전체 workflow를 정의
"""
from langgraph.graph import StateGraph, END
from graph_state import ResearchState
from graph_nodes import (
    web_crawler_node,
    similarity_node,
    summarization_node,
    report_node
)
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_research_graph():
    """
    연구 시스템의 LangGraph workflow 생성

    Returns:
        Compiled StateGraph
    """
    # StateGraph 초기화
    workflow = StateGraph[ResearchState, None, ResearchState, ResearchState](ResearchState)

    # 노드 추가
    workflow.add_node("web_crawler", web_crawler_node)
    workflow.add_node("similarity", similarity_node)
    workflow.add_node("summarization", summarization_node)
    workflow.add_node("report", report_node)

    # Edge 연결 (순차적 실행)
    workflow.set_entry_point("web_crawler")
    workflow.add_edge("web_crawler", "similarity")
    workflow.add_edge("similarity", "summarization")
    workflow.add_edge("summarization", "report")
    workflow.add_edge("report", END)

    # Graph 컴파일
    app = workflow.compile()

    return app


def run_research_workflow(urls, query_keywords, config):
    """
    연구 workflow 실행

    Args:
        urls: List[str] - 크롤링할 URL 목록
        query_keywords: List[Tuple[str, str]] - [(키워드, 설명), ...]
        config: Dict[str, Any] - 시스템 설정

    Returns:
        Dict[str, Any] - 실행 결과
    """
    start_time = time.time()

    logger.info("=" * 80)
    logger.info("LangGraph Multi-Agent Research System 시작")
    logger.info("=" * 80)

    # 초기 상태 설정
    initial_state = {
        'urls': urls,
        'query_keywords': query_keywords,
        'config': config,
        'crawled_data': None,
        'filtered_data': None,
        'groups': None,
        'report_path': None,
        'metadata': {},
        'errors': [],
        'success': True
    }

    # Graph 생성
    app = create_research_graph()

    try:
        # Workflow 실행
        final_state = app.invoke(initial_state)

        # 실행 시간 추가
        elapsed_time = time.time() - start_time
        final_state['metadata']['processing_time'] = elapsed_time

        # 성공 여부 확인
        has_errors = len(final_state.get('errors', [])) > 0
        final_state['success'] = not has_errors and final_state.get('report_path') is not None

        logger.info("\n" + "=" * 80)
        if final_state['success']:
            logger.info(f"모든 작업 완료! (소요 시간: {elapsed_time:.2f}초)")
        else:
            logger.error("일부 작업이 실패했습니다.")
            for error in final_state.get('errors', []):
                logger.error(f"  - {error}")
        logger.info("=" * 80)

        return final_state

    except Exception as e:
        logger.error(f"Workflow 실행 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

        elapsed_time = time.time() - start_time
        return {
            'success': False,
            'error': str(e),
            'metadata': {'processing_time': elapsed_time},
            'errors': [str(e)]
        }


def visualize_graph(output_path="outputs/workflow_graph.png"):
    """
    Graph를 시각화하여 이미지로 저장

    Args:
        output_path: str - 출력 이미지 경로
    """
    try:
        app = create_research_graph()

        # Mermaid diagram으로 출력
        graph_diagram = app.get_graph().draw_mermaid()

        logger.info("Graph 구조 (Mermaid):")
        logger.info(graph_diagram)

        return graph_diagram

    except Exception as e:
        logger.error(f"Graph 시각화 실패: {str(e)}")
        return None


if __name__ == "__main__":
    # 테스트용 코드
    print("LangGraph Workflow 테스트")

    # Graph 시각화
    visualize_graph()

    # 간단한 테스트
    test_urls = ["https://example.com"]
    test_keywords = [("AI", "인공지능 관련 내용")]
    test_config = {
        'crawler_max_depth': 1,
        'crawler_max_pages': 10,
        'similarity_threshold': 0.3,
        'use_transformer': False,
        'use_llm': False,
        'output_dir': 'outputs'
    }

    print("\n테스트 실행...")
    # result = run_research_workflow(test_urls, test_keywords, test_config)
    # print(f"\n결과: {result.get('success')}")
