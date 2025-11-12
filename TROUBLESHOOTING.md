# Troubleshooting Guide

## 웹 크롤링 문제 해결

### 문제: "HTTP None 오류" 또는 "403 Forbidden"

많은 웹사이트들이 봇 크롤링을 차단합니다. 특히 OpenAI, Anthropic, DeepMind 등의 AI 관련 웹사이트는 robots.txt를 통해 크롤링을 제한합니다.

---

## 해결 방법

### 1. 크롤링 가능한 대체 URL 사용 (권장)

다음 URL들은 크롤링이 가능하며 AI 관련 최신 정보를 제공합니다:

#### AI Research & News
```
https://arxiv.org/list/cs.AI/recent
https://huggingface.co/blog
https://paperswithcode.com/latest
https://machinelearningmastery.com/blog/
https://blog.research.google/
https://ai.meta.com/blog/
https://www.deepmind.com/blog
```

#### Tech News & Analysis
```
https://techcrunch.com/category/artificial-intelligence/
https://www.technologyreview.com/topic/artificial-intelligence/
https://venturebeat.com/category/ai/
https://www.theverge.com/ai-artificial-intelligence
```

#### Developer Communities
```
https://news.ycombinator.com/
https://dev.to/t/ai
https://medium.com/tag/artificial-intelligence
```

#### Academic & Publications
```
https://blog.ml.cmu.edu/
https://ai.stanford.edu/blog/
https://bair.berkeley.edu/blog/
https://distill.pub/
```

---

### 2. RSS 피드 사용

많은 웹사이트가 RSS 피드를 제공합니다:

```
# OpenAI 블로그 RSS
https://openai.com/blog/rss.xml

# Anthropic 뉴스 RSS
https://www.anthropic.com/news.rss

# Hugging Face 블로그 RSS
https://huggingface.co/blog/feed.xml
```

**사용 방법**:
```bash
# urls.txt에 RSS URL 추가
echo "https://openai.com/blog/rss.xml" > inputs/urls.txt
python main.py --depth 0
```

---

### 3. 크롤링 깊이 조정

메인 페이지만 크롤링하려면:

```bash
python main.py --depth 0 --max-pages 10
```

---

### 4. robots.txt 확인

웹사이트의 크롤링 정책을 확인하세요:

```bash
# 예시
curl https://openai.com/robots.txt
```

**OpenAI robots.txt 결과**:
```
User-agent: *
Disallow: /
```
→ 모든 크롤링 차단

**Hugging Face robots.txt 결과**:
```
User-agent: *
Allow: /
```
→ 크롤링 허용

---

## 추천 입력 파일 예시

### inputs/urls.txt (크롤링 가능한 URL)

```
# AI Research
https://huggingface.co/blog
https://paperswithcode.com/latest
https://arxiv.org/list/cs.AI/recent

# Tech News
https://techcrunch.com/category/artificial-intelligence/
https://venturebeat.com/category/ai/

# Academic Blogs
https://bair.berkeley.edu/blog/
https://ai.stanford.edu/blog/
```

### inputs/keywords.txt

```
AI model : 최신 AI 모델 발표 및 성능
LLM : Large Language Model 관련 동향
transformer : Transformer 아키텍처 발전
multimodal : 멀티모달 AI 기술
GPT : GPT 시리즈 업데이트
Claude : Anthropic Claude 모델
fine-tuning : 모델 파인튜닝 기법
RLHF : Reinforcement Learning from Human Feedback
```

---

## 실행 예시

### 기본 실행 (크롤링 가능한 URL 사용)

```bash
# 1. urls.txt 업데이트
cat > inputs/urls.txt << EOF
https://huggingface.co/blog
https://paperswithcode.com/latest
https://techcrunch.com/category/artificial-intelligence/
EOF

# 2. 실행
python main.py --depth 2 --max-pages 30 --threshold 0.3
```

### RSS 피드 사용

```bash
# 1. RSS URL 설정
cat > inputs/urls.txt << EOF
https://openai.com/blog/rss.xml
https://www.anthropic.com/news.rss
https://huggingface.co/blog/feed.xml
EOF

# 2. 깊이 0으로 실행 (RSS는 단일 페이지)
python main.py --depth 0 --max-pages 20
```

### 빠른 테스트

```bash
# 최소 설정으로 빠르게 테스트
python main.py --depth 1 --max-pages 5 --threshold 0.2
```

---

## 에러 메시지별 해결 방법

### "403 Forbidden - 접근 차단된 URL"

**원인**: 웹사이트가 봇 크롤링을 차단

**해결**:
1. 다른 크롤링 가능한 URL 사용 (위 목록 참고)
2. RSS 피드 사용
3. 웹사이트의 공식 API 사용 (있는 경우)

---

### "타임아웃으로 인해 건너뜀"

**원인**: 네트워크 느림, 서버 응답 지연

**해결**:
```bash
# 페이지 수를 줄이고 재시도
python main.py --max-pages 20
```

---

### "연결 오류"

**원인**: 네트워크 문제, 잘못된 URL

**해결**:
1. URL이 올바른지 확인
2. 네트워크 연결 확인
3. 방화벽/프록시 설정 확인

---

### "SSL 인증서 오류"

**원인**: SSL 인증서 문제

**해결**:
- 대부분의 경우 URL이 잘못되었거나 웹사이트 문제입니다
- 다른 URL을 시도하세요

---

## 크롤링 성능 최적화

### 빠른 크롤링

```bash
# 얕은 깊이, 적은 페이지, 낮은 임계값
python main.py \
  --depth 1 \
  --max-pages 20 \
  --threshold 0.2
```

### 정확한 크롤링

```bash
# 깊은 깊이, 많은 페이지, 높은 임계값, Transformer 사용
python main.py \
  --depth 3 \
  --max-pages 100 \
  --threshold 0.4 \
  --use-transformer
```

### 균형잡힌 설정 (권장)

```bash
python main.py \
  --depth 2 \
  --max-pages 50 \
  --threshold 0.3
```

---

## 로그 분석

### 성공적인 크롤링

```
2025-11-12 19:30:45 - WebCrawlerAgent - INFO - 크롤링 시작 - URLs: 3, Keywords: ['AI', 'LLM']
2025-11-12 19:30:46 - WebCrawlerAgent - INFO - 관련 콘텐츠 발견 (관련도: 0.85): Latest AI Models
2025-11-12 19:30:47 - WebCrawlerAgent - INFO - 관련 콘텐츠 발견 (관련도: 0.72): LLM Trends
2025-11-12 19:30:50 - WebCrawlerAgent - INFO - 크롤링 완료 - 총 15개 페이지 수집
```

### 실패하는 크롤링

```
2025-11-12 19:21:22 - WebCrawlerAgent - ERROR - HTTP None 오류: https://openai.com/blog
2025-11-12 19:21:22 - WebCrawlerAgent - INFO - 크롤링 완료 - 총 0개 페이지 수집
```
→ URL을 크롤링 가능한 대체 URL로 변경하세요

---

## 자주 묻는 질문 (FAQ)

### Q: 특정 웹사이트만 크롤링하고 싶어요

A: urls.txt에 해당 웹사이트만 추가하세요:
```bash
echo "https://huggingface.co/blog" > inputs/urls.txt
```

---

### Q: 크롤링 속도가 너무 느려요

A: 다음 방법을 시도하세요:
1. `--max-pages`를 줄이세요 (예: 20)
2. `--depth`를 줄이세요 (예: 1)
3. `--use-transformer` 옵션 제거 (키워드 기반이 더 빠름)

---

### Q: 수집되는 페이지가 너무 적어요

A: 다음 방법을 시도하세요:
1. `--threshold`를 낮추세요 (예: 0.2)
2. keywords.txt에 더 다양한 키워드 추가
3. urls.txt에 더 많은 URL 추가

---

### Q: 결과의 관련성이 낮아요

A: 다음 방법을 시도하세요:
1. `--threshold`를 높이세요 (예: 0.5)
2. `--use-transformer` 옵션 사용 (더 정확한 유사도)
3. keywords.txt의 설명을 더 구체적으로 작성

---

## 모범 사례

### 1. 크롤링 가능한 URL 사용

✅ **좋은 예**:
```
https://huggingface.co/blog
https://paperswithcode.com/latest
https://arxiv.org/list/cs.AI/recent
```

❌ **나쁜 예**:
```
https://openai.com/blog        # 크롤링 차단
https://www.anthropic.com/news # 크롤링 차단
```

---

### 2. 적절한 크롤링 깊이 설정

- **깊이 0-1**: RSS 피드, 단일 페이지
- **깊이 2**: 블로그, 뉴스 사이트 (권장)
- **깊이 3+**: 대형 문서 사이트 (느림)

---

### 3. 키워드 최적화

✅ **좋은 예**:
```
AI model : 최신 발표된 AI 모델의 성능과 벤치마크 결과
LLM training : Large Language Model의 학습 방법과 데이터셋
```

❌ **나쁜 예**:
```
AI : AI
model : model
```

---

### 4. 점진적 테스트

```bash
# 1단계: 빠른 테스트
python main.py --depth 1 --max-pages 5

# 2단계: 중간 테스트
python main.py --depth 2 --max-pages 20

# 3단계: 전체 실행
python main.py --depth 2 --max-pages 50
```

---

## 지원

문제가 계속되면:

1. **로그 확인**: 에러 메시지에서 구체적인 문제 파악
2. **설정 조정**: `--depth`, `--max-pages`, `--threshold` 변경
3. **URL 변경**: 크롤링 가능한 대체 URL 사용
4. **Issue 생성**: GitHub에 상세한 에러 로그와 함께 issue 생성

---

## 참고 자료

- [robots.txt 표준](https://www.robotstxt.org/)
- [웹 스크래핑 윤리](https://en.wikipedia.org/wiki/Web_scraping#Legal_issues)
- [RSS 피드란?](https://en.wikipedia.org/wiki/RSS)
- [User-Agent 헤더](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent)

---

**마지막 업데이트**: 2025-11-12
