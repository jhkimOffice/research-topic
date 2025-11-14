"""
Report Agent
요약된 정보를 기반으로 마크다운 형식의 보고서 생성
"""
from typing import Dict, List, Any, Tuple
from datetime import datetime
from agents.base_agent import BaseAgent
import os


class ReportAgent(BaseAgent):
    """보고서 생성 에이전트"""

    def __init__(self, output_dir: str = "outputs"):
        super().__init__("ReportAgent")
        self.output_dir = output_dir

        # 출력 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)

    def execute(self, input_data: Dict) -> Dict[str, Any]:
        """
        보고서 생성 실행

        Args:
            input_data: {
                'groups': List[Dict],  # 요약된 그룹 데이터
                'query_keywords': List[Tuple[str, str]],
                'metadata': Dict  # 메타데이터 (URL 수, 크롤링 시간 등)
            }

        Returns:
            Dict[str, Any]: {
                'success': bool,
                'report_path': str,  # 생성된 보고서 경로
                'report_content': str  # 보고서 내용
            }
        """
        groups = input_data.get('groups', [])
        query_keywords = input_data.get('query_keywords', [])
        metadata = input_data.get('metadata', {})

        self.log_info("보고서 생성 시작")

        # 마크다운 보고서 생성
        report_content = self._generate_markdown_report(groups, query_keywords, metadata)

        use_terminal_output = True # debugging
        if use_terminal_output:
            print(report_content)
            return {
                'success': True,
                'report_path': "Terminal Output",
                'report_content': report_content
            }
        else:
            # 파일로 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"research_report_{timestamp}.md"
            report_path = os.path.join(self.output_dir, report_filename)

            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)

            self.log_info(f"보고서 생성 완료: {report_path}")

            return {
                'success': True,
                'report_path': report_path,
                'report_content': report_content
            }

    def _generate_markdown_report(self, groups: List[Dict], query_keywords: List[Tuple[str, str]], metadata: Dict) -> str:
        """마크다운 형식의 보고서 생성"""
        lines = []

        # 헤더
        lines.append("# 리서치 분석 보고서")
        lines.append("")
        lines.append(f"**생성 일시:** {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}")
        lines.append("")

        # 메타데이터
        lines.append("## 분석 개요")
        lines.append("")
        lines.append(f"- **분석 URL 수:** {metadata.get('total_urls', 0)}")
        lines.append(f"- **크롤링된 페이지 수:** {metadata.get('crawled_pages', 0)}")
        lines.append(f"- **필터링된 페이지 수:** {metadata.get('filtered_pages', 0)}")
        lines.append(f"- **그룹 수:** {len(groups)}")
        lines.append("")

        # 검색 키워드
        lines.append("## 검색 키워드")
        lines.append("")
        for keyword, description in query_keywords:
            lines.append(f"### {keyword}")
            lines.append(f"> {description}")
            lines.append("")

        # 구분선
        lines.append("---")
        lines.append("")

        # 주요 발견사항
        lines.append("## 주요 발견사항")
        lines.append("")

        if not groups:
            lines.append("분석 결과가 없습니다.")
        else:
            # 각 그룹별 요약
            for i, group in enumerate(groups, 1):
                keyword = group.get('keyword', '알 수 없음')
                description = group.get('description', '')
                summary = group.get('summary', '')
                items = group.get('items', [])

                lines.append(f"### {i}. {keyword}")
                lines.append("")

                if description:
                    lines.append(f"**관심 사항:** {description}")
                    lines.append("")

                lines.append(f"**관련 문서 수:** {len(items)}개")
                lines.append("")

                lines.append("**요약:**")
                lines.append("")
                lines.append(summary)
                lines.append("")

                # 상위 문서 목록
                lines.append("**주요 참고 자료:**")
                lines.append("")

                for j, item in enumerate(items[:5], 1):  # 상위 5개만 표시
                    title = item.get('title', '제목 없음')
                    url = item.get('url', '#')
                    similarity = item.get('similarity_score', 0)

                    lines.append(f"{j}. [{title}]({url})")
                    lines.append(f"   - 관련도: {similarity:.2%}")
                    lines.append("")

                lines.append("---")
                lines.append("")

        # 상세 내용 (Appendix)
        lines.append("## 부록: 상세 내용")
        lines.append("")

        for i, group in enumerate(groups, 1):
            keyword = group.get('keyword', '알 수 없음')
            items = group.get('items', [])

            lines.append(f"### A{i}. {keyword} 상세 내용")
            lines.append("")

            for j, item in enumerate(items, 1):
                title = item.get('title', '제목 없음')
                url = item.get('url', '#')
                content = item.get('content', '')

                lines.append(f"#### A{i}.{j}. {title}")
                lines.append("")
                lines.append(f"**URL:** {url}")
                lines.append("")
                lines.append("**내용:**")
                lines.append("")
                # 콘텐츠를 적절히 잘라서 표시
                preview = content[:1000] + "..." if len(content) > 1000 else content
                lines.append(preview)
                lines.append("")
                lines.append("---")
                lines.append("")

        # 푸터
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*본 보고서는 AI Multi-Agent 시스템에 의해 자동 생성되었습니다.*")

        return "\n".join(lines)
