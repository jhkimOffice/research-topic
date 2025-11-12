# Multi-Agent Research System (LangGraph)

Python 기반 AI Multi-Agent 시스템으로, **LangGraph**를 사용하여 웹 크롤링, 유사도 분석, 요약, 보고서 생성을 자동화합니다.

## 시스템 아키텍처

이 시스템은 **LangGraph**를 사용하여 4개의 전문화된 에이전트를 순차적으로 실행합니다:

### LangGraph Workflow
```
START → Web Crawler → Similarity → Summarization → Report → END
```

### Agent 설명

1. **Web Crawler Node**: URL을 크롤링하고 키워드 관련 콘텐츠를 수집
2. **Similarity Node**: 수집된 콘텐츠의 유사도를 분석하고 필터링
3. **Summarization Node**: 관련 콘텐츠를 그룹화하고 요약
4. **Report Node**: 마크다운 형식의 보고서 생성

### LangGraph의 장점

- **명확한 Workflow 시각화**: 전체 프로세스를 그래프로 표현
- **상태 기반 데이터 관리**: TypedDict를 사용한 타입 안전성
- **디버깅 용이**: 각 노드의 입출력 추적 가능
- **확장성**: 새로운 노드 추가 및 조건부 라우팅 쉬움

## 프로젝트 구조

```
research-topic/
├── agents/                      # 에이전트 모듈
│   ├── __init__.py
│   ├── base_agent.py           # 기본 에이전트 클래스
│   ├── web_crawler_agent.py    # 웹 크롤러
│   ├── similarity_agent.py     # 유사도 분석
│   ├── summarization_agent.py  # 요약
│   └── report_agent.py         # 보고서 생성
├── inputs/                      # 입력 파일
│   ├── urls.txt                # 크롤링할 URL 목록
│   └── keywords.txt            # 검색 키워드 및 설명
├── outputs/                     # 출력 파일 (자동 생성)
│   └── research_report_*.md    # 생성된 보고서
├── graph_state.py              # LangGraph 상태 정의
├── graph_nodes.py              # LangGraph 노드 함수
├── graph_workflow.py           # LangGraph 워크플로우
├── config.py                   # 설정 파일
├── utils.py                    # 유틸리티 함수
├── main.py                     # 메인 실행 파일
├── pyproject.toml              # 프로젝트 설정 및 의존성
└── README.md                   # 이 파일
```

## 설치 방법

### 1. 저장소 클론 (또는 파일 다운로드)

```bash
cd research-topic
```

### 2. 가상환경 생성 (권장)

```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. 패키지 설치

**기본 설치 (권장):**
```bash
# uv 사용
uv sync

# 또는 pip 사용
pip install -e .
```

기본 설치는 다음 패키지를 포함합니다:
- LangGraph (워크플로우 관리)
- LangChain (LLM 통합)
- Requests, BeautifulSoup4 (웹 크롤링)

**선택적 기능 설치:**

Transformer 기반 유사도 분석을 사용하려면:
```bash
# uv 사용
uv sync --extra transformer

# 또는 pip 사용
pip install -e ".[transformer]"
```

OpenAI LLM 요약을 사용하려면:
```bash
# uv 사용
uv sync --extra llm

# 또는 pip 사용
pip install -e ".[llm]"
```

모든 기능 설치:
```bash
# uv 사용
uv sync --extra all

# 또는 pip 사용
pip install -e ".[all]"
```

OpenAI API를 사용하려면 환경 변수 설정이 필요합니다:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

또는 `.env` 파일 생성:
```
OPENAI_API_KEY=your-api-key-here
```

## 사용 방법

### 1. 입력 파일 준비

#### `inputs/urls.txt` - 크롤링할 URL 목록
```
https://openai.com/blog
https://www.anthropic.com/news
https://deepmind.google/discover/blog/
```

#### `inputs/keywords.txt` - 키워드와 설명
```
AI model : 최신 릴리즈 혹은 발표된 AI 모델과 뛰어난 성능을 보이는 분야
GPT : GPT 시리즈 모델의 최신 동향과 활용 사례
Claude : Anthropic의 Claude 모델 관련 소식과 기능 업데이트
```

형식: `키워드 : 설명`

### 2. 기본 실행

```bash
python main.py
```

### 3. 옵션을 사용한 실행

```bash
# 크롤링 깊이 설정
python main.py --depth 3

# 최대 페이지 수 설정
python main.py --max-pages 100

# 유사도 임계값 설정 (0.0 ~ 1.0)
python main.py --threshold 0.5

# Transformer 모델 사용 (더 정확하지만 느림)
python main.py --use-transformer

# LLM 요약 사용 (OpenAI API 키 필요)
python main.py --use-llm

# LangGraph workflow 시각화
python main.py --visualize

# 모든 옵션 결합
python main.py --depth 2 --max-pages 50 --threshold 0.3 --use-transformer --visualize
```

### 4. 사용자 정의 입력 파일 사용

```bash
python main.py --urls my_urls.txt --keywords my_keywords.txt
```

## 명령줄 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--urls` | URL 파일 경로 | `inputs/urls.txt` |
| `--keywords` | 키워드 파일 경로 | `inputs/keywords.txt` |
| `--depth` | 크롤링 깊이 (하위 페이지) | `2` |
| `--max-pages` | 최대 크롤링 페이지 수 | `50` |
| `--threshold` | 유사도 임계값 (0.0-1.0) | `0.3` |
| `--use-transformer` | Transformer 모델 사용 | `False` |
| `--use-llm` | LLM 요약 사용 | `False` |
| `--visualize` | LangGraph workflow 시각화 | `False` |

## 설정 파일 (`config.py`)

`config.py` 파일에서 기본 설정을 변경할 수 있습니다:

```python
class Config:
    # 파일 경로
    URLS_FILE = "inputs/urls.txt"
    KEYWORDS_FILE = "inputs/keywords.txt"
    OUTPUT_DIR = "outputs"

    # Web Crawler 설정
    CRAWLER_MAX_DEPTH = 2
    CRAWLER_MAX_PAGES = 50
    CRAWLER_DELAY = 1.0  # 초

    # Similarity Agent 설정
    SIMILARITY_THRESHOLD = 0.3
    USE_TRANSFORMER = False

    # Summarization Agent 설정
    USE_LLM = False
```

## 출력 결과

실행이 완료되면 `outputs/` 디렉토리에 마크다운 형식의 보고서가 생성됩니다:

```
outputs/research_report_20250111_143025.md
```

보고서에는 다음 내용이 포함됩니다:
- 분석 개요 및 통계
- 검색 키워드 목록
- 주요 발견사항 (그룹별 요약)
- 참고 자료 링크
- 상세 내용 (부록)

## LangGraph Node 상세 설명

### Web Crawler Node
- 지정된 URL의 하위 페이지를 재귀적으로 크롤링
- 키워드와 관련된 콘텐츠만 추출
- 같은 도메인 내에서만 크롤링 (외부 링크 제외)
- 서버 부하 방지를 위한 딜레이 적용
- **출력**: `crawled_data` (크롤링된 페이지 데이터)

### Similarity Node
- 키워드 기반 매칭 (기본)
- Transformer 기반 의미적 유사도 (옵션)
- 임계값 이하의 콘텐츠 필터링
- **입력**: `crawled_data`
- **출력**: `filtered_data` (필터링된 페이지)

### Summarization Node
- 키워드별 콘텐츠 그룹화
- 추출 기반 요약 (기본)
- LLM 기반 추상적 요약 (옵션)
- **입력**: `filtered_data`
- **출력**: `groups` (그룹화된 요약)

### Report Node
- 마크다운 형식의 구조화된 보고서
- 그룹별 요약 및 참고 자료
- 상세 내용 부록
- **입력**: `groups`
- **출력**: `report_path` (보고서 파일 경로)

## 예시 사용 시나리오

### AI 모델 연구
```bash
# inputs/keywords.txt
AI model : 최신 릴리즈 혹은 발표된 AI 모델과 뛰어난 성능을 보이는 분야
GPT-4 : GPT-4 모델의 성능과 활용 사례
multimodal : 멀티모달 AI 모델의 발전

# inputs/urls.txt
https://openai.com/blog
https://www.anthropic.com/news

# 실행
python main.py --depth 2 --max-pages 50
```

## 문제 해결

### 403 Forbidden 에러

일부 웹사이트(특히 OpenAI, Anthropic 등)는 봇 크롤링을 차단합니다.

**해결 방법:**

1. **다른 URL 사용**: 크롤링 친화적인 사이트를 선택하세요
   ```
   # 대안 URL 예시 (inputs/urls.txt)
   https://arxiv.org/list/cs.AI/recent
   https://huggingface.co/blog
   https://machinelearningmastery.com/blog/
   https://towardsdatascience.com/
   ```

2. **Depth를 0으로 설정**: 메인 페이지만 크롤링
   ```bash
   python main.py --depth 0
   ```

3. **RSS 피드 사용**: 웹사이트의 RSS 피드 URL을 사용하세요
   ```
   https://openai.com/blog/rss.xml
   https://www.anthropic.com/rss.xml
   ```

**중요**: 웹사이트의 robots.txt와 이용약관을 항상 확인하고 준수하세요.

### ImportError: No module named 'sentence_transformers'
```bash
pip install sentence-transformers torch
```

### ImportError: No module named 'openai'
```bash
pip install openai
```

### 크롤링이 너무 느림
- `--max-pages` 값을 줄이세요
- `--depth` 값을 줄이세요
- `config.py`의 `CRAWLER_DELAY`를 줄이세요 (권장하지 않음)

### 유사도 점수가 너무 낮음
- `--threshold` 값을 낮추세요
- `--use-transformer` 옵션을 사용하세요

### OpenAI API 오류
- API 키가 올바르게 설정되었는지 확인하세요
- API 사용량 한도를 확인하세요

## 주의사항

1. **웹 크롤링 규칙 준수**: robots.txt 및 웹사이트 이용 약관을 확인하세요
2. **API 비용**: OpenAI API 사용 시 비용이 발생할 수 있습니다
3. **서버 부하**: 크롤링 딜레이를 적절히 설정하여 서버에 부하를 주지 마세요
4. **개인정보**: 수집된 데이터의 개인정보 처리에 주의하세요

## 라이선스

이 프로젝트는 교육 및 연구 목적으로 제작되었습니다.

## 기여

버그 리포트 및 기능 제안은 환영합니다!

## 연락처

문의사항이 있으시면 이슈를 등록해주세요.
