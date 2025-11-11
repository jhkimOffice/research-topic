"""
Summarization Agent
필터링된 콘텐츠를 그룹화하고 요약
"""
from typing import Dict, List, Any
from collections import defaultdict
from agents.base_agent import BaseAgent
import re


class SummarizationAgent(BaseAgent):
    """요약 에이전트"""

    def __init__(self, use_llm: bool = False, api_key: str = None):
        super().__init__("SummarizationAgent")
        self.use_llm = use_llm
        self.api_key = api_key
        self.client = None

        if use_llm and api_key:
            try:
                import openai
                self.client = openai.OpenAI(api_key=api_key)
                self.log_info("OpenAI API 클라이언트 초기화 완료")
            except ImportError:
                self.log_warning("openai 라이브러리 미설치. 추출 기반 요약 사용")
                self.use_llm = False
            except Exception as e:
                self.log_error(f"OpenAI 초기화 실패: {str(e)}")
                self.use_llm = False

    def execute(self, input_data: Dict) -> Dict[str, Any]:
        """
        콘텐츠 그룹화 및 요약 실행

        Args:
            input_data: {
                'filtered_data': Dict[str, Dict],  # 필터링된 데이터
                'query_keywords': List[Tuple[str, str]]  # [(키워드, 설명), ...]
            }

        Returns:
            Dict[str, Any]: {
                'success': bool,
                'groups': List[Dict],  # 그룹화된 요약 결과
            }
        """
        filtered_data = input_data.get('filtered_data', {})
        query_keywords = input_data.get('query_keywords', [])

        self.log_info(f"요약 시작 - 페이지 수: {len(filtered_data)}")

        if not filtered_data:
            return {'success': False, 'groups': []}

        # 콘텐츠 그룹화
        groups = self._group_content(filtered_data, query_keywords)

        # 각 그룹 요약
        summarized_groups = []
        for i, group in enumerate(groups):
            self.log_info(f"그룹 {i+1} 요약 중... (문서 {len(group['items'])}개)")
            summary = self._summarize_group(group)
            summarized_groups.append(summary)

        self.log_info(f"요약 완료 - 총 {len(summarized_groups)}개 그룹")

        return {
            'success': True,
            'groups': summarized_groups,
            'total_groups': len(summarized_groups)
        }

    def _group_content(self, filtered_data: Dict, query_keywords: List[Tuple[str, str]]) -> List[Dict]:
        """콘텐츠를 주제별로 그룹화"""
        # 키워드별 그룹 생성
        keyword_groups = defaultdict(list)

        for url, data in filtered_data.items():
            title = data.get('title', '')
            content = data.get('content', '')
            text = (title + " " + content).lower()

            # 어떤 키워드와 가장 관련있는지 찾기
            best_keyword = None
            best_score = 0

            for keyword, description in query_keywords:
                score = text.count(keyword.lower())
                # 설명의 주요 단어도 체크
                desc_words = re.findall(r'\b\w{3,}\b', description.lower())
                for word in desc_words:
                    score += text.count(word) * 0.5

                if score > best_score:
                    best_score = score
                    best_keyword = keyword

            # 관련 키워드가 없으면 "기타"로 분류
            if best_keyword is None:
                best_keyword = "기타"

            keyword_groups[best_keyword].append({
                'url': url,
                'title': title,
                'content': content,
                'similarity_score': data.get('similarity_score', 0)
            })

        # 그룹 리스트로 변환
        groups = []
        for keyword, items in keyword_groups.items():
            # 유사도 점수로 정렬
            items.sort(key=lambda x: x['similarity_score'], reverse=True)

            # 키워드에 해당하는 설명 찾기
            description = ""
            for kw, desc in query_keywords:
                if kw == keyword:
                    description = desc
                    break

            groups.append({
                'keyword': keyword,
                'description': description,
                'items': items,
                'item_count': len(items)
            })

        # 아이템 수로 정렬 (많은 순)
        groups.sort(key=lambda x: x['item_count'], reverse=True)

        return groups

    def _summarize_group(self, group: Dict) -> Dict:
        """그룹 요약 생성"""
        keyword = group['keyword']
        description = group['description']
        items = group['items']

        if self.use_llm and self.client:
            summary_text = self._llm_summarize(keyword, description, items)
        else:
            summary_text = self._extractive_summarize(keyword, description, items)

        return {
            'keyword': keyword,
            'description': description,
            'summary': summary_text,
            'items': items,
            'item_count': len(items)
        }

    def _llm_summarize(self, keyword: str, description: str, items: List[Dict]) -> str:
        """LLM을 사용한 추상적 요약"""
        try:
            # 콘텐츠 준비
            content_text = f"키워드: {keyword}\n설명: {description}\n\n관련 문서들:\n\n"
            for i, item in enumerate(items[:10], 1):  # 최대 10개만 사용
                content_text += f"{i}. {item['title']}\n{item['content'][:500]}...\n\n"

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 기술 문서를 요약하는 전문가입니다. 주어진 문서들을 읽고 핵심 내용을 3-5개의 bullet point로 요약해주세요."},
                    {"role": "user", "content": content_text}
                ],
                max_tokens=500,
                temperature=0.3
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            self.log_error(f"LLM 요약 실패: {str(e)}, 추출 기반 요약으로 전환")
            return self._extractive_summarize(keyword, description, items)

    def _extractive_summarize(self, keyword: str, description: str, items: List[Dict]) -> str:
        """추출 기반 요약 (키워드 주변 문장 추출)"""
        summary_sentences = []

        # 키워드와 관련된 중요 문장 추출
        for item in items[:5]:  # 상위 5개 문서만 사용
            content = item['content']
            # 문장 분리
            sentences = re.split(r'[.!?]\s+', content)

            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) < 20 or len(sentence) > 300:
                    continue

                # 키워드 포함 여부 확인
                if keyword.lower() in sentence.lower():
                    # 중복 체크
                    if sentence not in summary_sentences:
                        summary_sentences.append(sentence)
                        if len(summary_sentences) >= 5:
                            break

            if len(summary_sentences) >= 5:
                break

        if summary_sentences:
            return "\n• " + "\n• ".join(summary_sentences[:5])
        else:
            # 키워드 관련 문장이 없으면 각 문서의 첫 문장 사용
            for item in items[:3]:
                first_sentence = item['content'][:200].split('.')[0]
                if first_sentence:
                    summary_sentences.append(f"{item['title']}: {first_sentence}")

            return "\n• " + "\n• ".join(summary_sentences) if summary_sentences else "요약 내용이 없습니다."
