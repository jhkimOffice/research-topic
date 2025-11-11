"""
Orchestrator Agent
모든 에이전트를 조정하고 워크플로우를 관리
"""
from typing import Dict, Any
from agents.base_agent import BaseAgent
from agents.web_crawler_agent import WebCrawlerAgent
from agents.similarity_agent import SimilarityAgent
from agents.summarization_agent import SummarizationAgent
from agents.report_agent import ReportAgent
import time


class OrchestratorAgent(BaseAgent):
    """오케스트레이터 에이전트 - 모든 에이전트를 조정"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__("OrchestratorAgent")
        self.config = config

        # 각 에이전트 초기화
        self.log_info("에이전트 초기화 중...")

        self.web_crawler = WebCrawlerAgent(
            max_depth=config.get('crawler_max_depth', 2),
            max_pages=config.get('crawler_max_pages', 50),
            delay=config.get('crawler_delay', 1.0)
        )

        self.similarity_agent = SimilarityAgent(
            similarity_threshold=config.get('similarity_threshold', 0.3),
            use_transformer=config.get('use_transformer', False)
        )

        self.summarization_agent = SummarizationAgent(
            use_llm=config.get('use_llm', False),
            api_key=config.get('openai_api_key', None)
        )

        self.report_agent = ReportAgent(
            output_dir=config.get('output_dir', 'outputs')
        )

        self.log_info("모든 에이전트 초기화 완료")

    def execute(self, input_data: Dict) -> Dict[str, Any]:
        """
        전체 워크플로우 실행

        Args:
            input_data: {
                'urls': List[str],  # 크롤링할 URL 목록
                'query_keywords': List[Tuple[str, str]]  # [(키워드, 설명), ...]
            }

        Returns:
            Dict[str, Any]: {
                'success': bool,
                'report_path': str,
                'metadata': Dict
            }
        """
        start_time = time.time()

        self.log_info("=" * 80)
        self.log_info("Multi-Agent Research System 시작")
        self.log_info("=" * 80)

        urls = input_data.get('urls', [])
        query_keywords = input_data.get('query_keywords', [])

        if not urls:
            self.log_error("URL이 제공되지 않았습니다.")
            return {'success': False, 'error': 'No URLs provided'}

        if not query_keywords:
            self.log_error("키워드가 제공되지 않았습니다.")
            return {'success': False, 'error': 'No keywords provided'}

        try:
            # Step 1: Web Crawling
            self.log_info("\n[1/4] Web Crawler Agent 실행")
            self.log_info("-" * 80)

            keywords = [kw for kw, _ in query_keywords]
            crawler_result = self.web_crawler.execute({
                'urls': urls,
                'keywords': keywords
            })

            if not crawler_result.get('success'):
                self.log_error("웹 크롤링 실패")
                return {'success': False, 'error': 'Web crawling failed'}

            crawled_data = crawler_result.get('data', {})
            self.log_info(f"✓ 크롤링 완료: {len(crawled_data)}개 페이지 수집")

            # Step 2: Similarity Analysis
            self.log_info("\n[2/4] Similarity Agent 실행")
            self.log_info("-" * 80)

            similarity_result = self.similarity_agent.execute({
                'crawled_data': crawled_data,
                'query_keywords': query_keywords
            })

            if not similarity_result.get('success'):
                self.log_error("유사도 분석 실패")
                return {'success': False, 'error': 'Similarity analysis failed'}

            filtered_data = similarity_result.get('filtered_data', {})
            self.log_info(f"✓ 유사도 분석 완료: {len(filtered_data)}개 페이지 선택")

            # Step 3: Summarization
            self.log_info("\n[3/4] Summarization Agent 실행")
            self.log_info("-" * 80)

            summarization_result = self.summarization_agent.execute({
                'filtered_data': filtered_data,
                'query_keywords': query_keywords
            })

            if not summarization_result.get('success'):
                self.log_error("요약 실패")
                return {'success': False, 'error': 'Summarization failed'}

            groups = summarization_result.get('groups', [])
            self.log_info(f"✓ 요약 완료: {len(groups)}개 그룹 생성")

            # Step 4: Report Generation
            self.log_info("\n[4/4] Report Agent 실행")
            self.log_info("-" * 80)

            metadata = {
                'total_urls': len(urls),
                'crawled_pages': len(crawled_data),
                'filtered_pages': len(filtered_data),
                'processing_time': time.time() - start_time
            }

            report_result = self.report_agent.execute({
                'groups': groups,
                'query_keywords': query_keywords,
                'metadata': metadata
            })

            if not report_result.get('success'):
                self.log_error("보고서 생성 실패")
                return {'success': False, 'error': 'Report generation failed'}

            report_path = report_result.get('report_path', '')
            self.log_info(f"✓ 보고서 생성 완료: {report_path}")

            # 완료
            elapsed_time = time.time() - start_time
            self.log_info("\n" + "=" * 80)
            self.log_info(f"모든 작업 완료! (소요 시간: {elapsed_time:.2f}초)")
            self.log_info("=" * 80)

            return {
                'success': True,
                'report_path': report_path,
                'metadata': {
                    **metadata,
                    'total_groups': len(groups),
                    'processing_time': elapsed_time
                }
            }

        except Exception as e:
            self.log_error(f"오케스트레이터 실행 중 오류 발생: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
