#!/usr/bin/env python3
"""
YAML → RAG Chunks 변환 스크립트

UMIS의 YAML 파일을 에이전트별 관점으로 청킹하여
RAG 시스템에 최적화된 JSON Lines 형식으로 변환합니다.

사용법:
    python scripts/01_convert_yaml.py

출력:
    ../../data/chunks/explorer_chunks.jsonl  (Explorer 전용 청크)
    ../../data/chunks/observer_chunks.jsonl (향후 확장)
    ...
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml
from rich.console import Console
from rich.progress import track

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from umis_rag.utils.logger import logger

console = Console()


class UMISYAMLConverter:
    """
    UMIS YAML 파일을 RAG용 청크로 변환하는 컨버터
    
    개념:
    ------
    1. **청킹 전략**: 에이전트별로 다른 관점으로 같은 데이터를 청킹
       - Explorer: 기회/전략 중심
       - Observer: 구조/패턴 중심 (향후)
       - Quantifier: 정량 데이터 중심 (향후)
    
    2. **메타데이터**: 각 청크에 검색 최적화를 위한 메타데이터 첨부
       - agent: 어느 에이전트용인가
       - pattern_id: 어떤 패턴인가
       - keywords: 검색 키워드
    
    3. **출력 형식**: JSON Lines (.jsonl)
       - 한 줄에 하나의 청크 (JSON 객체)
       - 스트리밍 처리 가능
       - 대용량 데이터 효율적
    """
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.raw_dir = data_dir / "raw"
        self.chunks_dir = data_dir / "chunks"
        self.chunks_dir.mkdir(exist_ok=True)
        
        logger.info(f"Converter 초기화: {self.raw_dir} → {self.chunks_dir}")
    
    def load_yaml(self, filename: str) -> Dict[str, Any]:
        """YAML 파일 로드"""
        filepath = self.raw_dir / filename
        logger.info(f"YAML 파일 로딩: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        logger.info(f"  ✅ {len(data)} 개 최상위 키 로드됨")
        return data
    
    def convert_business_model_patterns_for_explorer(self) -> List[Dict[str, Any]]:
        """
        비즈니스 모델 패턴을 Explorer 관점으로 청킹
        
        Explorer의 관심사:
        - 어떤 트리거 시그널이 이 패턴을 시사하는가?
        - 기회 구조는 무엇인가?
        - 검증 방법은?
        - 성공 사례는?
        
        청킹 전략:
        - 1개 패턴 = 여러 청크로 분할
        - 섹션별로 독립 청크 (concept, triggers, structure, validation, cases)
        """
        logger.info("📊 비즈니스 모델 패턴 → Explorer 청크 변환 시작")
        
        data = self.load_yaml("umis_business_model_patterns.yaml")
        chunks = []
        
        # 7개 패턴 ID
        pattern_ids = [
            "platform_business_model",
            "subscription_model",
            "franchise_model",
            "direct_to_consumer_model",
            "advertising_model",
            "licensing_model",
            "freemium_model"
        ]
        
        for pattern_id in track(pattern_ids, description="패턴 처리 중..."):
            if pattern_id not in data:
                logger.warning(f"  ⚠️  패턴 없음: {pattern_id}")
                continue
            
            pattern = data[pattern_id]
            
            # 청크 1: 패턴 개요 (Concept + Triggers)
            chunks.append(self._create_pattern_overview_chunk(pattern_id, pattern))
            
            # 청크 2: 기회 구조 (Opportunity Structure)
            if "opportunity_structure" in pattern:
                chunks.append(self._create_opportunity_structure_chunk(pattern_id, pattern))
            
            # 청크 3: 검증 프레임워크
            if "validation_framework" in pattern:
                chunks.append(self._create_validation_framework_chunk(pattern_id, pattern))
            
            # 청크 4-N: 성공 사례들 (각 사례별로 독립 청크)
            if "success_case_library" in pattern:
                chunks.extend(self._create_case_chunks(pattern_id, pattern))
        
        logger.info(f"  ✅ 총 {len(chunks)}개 Explorer 청크 생성")
        return chunks
    
    def _create_pattern_overview_chunk(
        self, 
        pattern_id: str, 
        pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        패턴 개요 청크 생성
        
        포함 내용:
        - Concept (핵심 개념)
        - Trigger Observations (트리거 시그널)
        
        Explorer가 사용하는 시나리오:
        "Observer가 '높은 초기 비용 + 정기 유지관리' 발견"
        → Explorer가 트리거 검색
        → subscription_model 매칭!
        """
        concept = pattern.get("concept", {})
        triggers = pattern.get("trigger_observations", {})
        
        # 청크 컨텐츠 구성
        content = f"""
## {concept.get('name', pattern_id)}

### 핵심 개념
- **본질**: {concept.get('essence', 'N/A')}
- **핵심 가치**: {concept.get('core_value', 'N/A')}

### 트리거 시그널 (Observer 관찰에서 찾을 신호)
"""
        
        # 트리거 시그널 추가
        if "signals" in triggers:
            for signal in triggers["signals"]:
                content += f"- {signal}\n"
        
        # 메타데이터 구성
        metadata = {
            "chunk_id": f"{pattern_id}_overview",
            "chunk_type": "pattern_overview",
            "agent": "explorer",
            "pattern_id": pattern_id,
            "pattern_type": "business_model",
            "section": "concept_and_triggers",
            
            # 검색 최적화
            "keywords": self._extract_keywords(concept),
            "triggers": triggers.get("signals", []) if isinstance(triggers.get("signals"), list) else [],
            
            # 메타 정보
            "source_file": "umis_business_model_patterns.yaml",
            "token_count": len(content.split()),  # 대략적 토큰 수
        }
        
        return {
            "content": content.strip(),
            "metadata": metadata
        }
    
    def _create_opportunity_structure_chunk(
        self, 
        pattern_id: str, 
        pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        기회 구조 청크 생성
        
        Explorer의 Phase 2 (다차원 분석)에서 사용
        - 가치 제안은?
        - 수익 모델은?
        - 구조적 요건은?
        """
        opp_structure = pattern["opportunity_structure"]
        
        content = f"""
## {pattern.get('concept', {}).get('name', pattern_id)} - 기회 구조

### 가치 제안
"""
        
        # 가치 제안 섹션 추가
        if "value_proposition" in opp_structure:
            vp = opp_structure["value_proposition"]
            for stakeholder, values in vp.items():
                content += f"\n**{stakeholder}**:\n"
                if isinstance(values, list):
                    for v in values:
                        content += f"- {v}\n"
        
        # 수익 모델
        if "revenue_models" in opp_structure:
            content += "\n### 수익 모델\n"
            for rev_model in opp_structure["revenue_models"]:
                if isinstance(rev_model, dict):
                    content += f"- **{rev_model.get('type', 'N/A')}**: {rev_model.get('mechanism', rev_model.get('structure', 'N/A'))}\n"
        
        # 구조적 요건
        if "structural_requirements" in opp_structure:
            content += "\n### 구조적 요건\n"
            content += yaml.dump(opp_structure["structural_requirements"], allow_unicode=True, default_flow_style=False)
        
        metadata = {
            "chunk_id": f"{pattern_id}_opportunity_structure",
            "chunk_type": "opportunity_structure",
            "agent": "explorer",
            "pattern_id": pattern_id,
            "pattern_type": "business_model",
            "section": "opportunity_structure",
            "source_file": "umis_business_model_patterns.yaml",
            "token_count": len(content.split()),
        }
        
        return {
            "content": content.strip(),
            "metadata": metadata
        }
    
    def _create_validation_framework_chunk(
        self, 
        pattern_id: str, 
        pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        검증 프레임워크 청크
        
        Explorer가 가설 생성 후 검증할 때 사용
        - Quantifier에게 뭘 물어봐야 하나?
        - Validator에게 뭘 확인해야 하나?
        - Observer에게 뭘 검증받아야 하나?
        """
        val_framework = pattern["validation_framework"]
        
        content = f"""
## {pattern.get('concept', {}).get('name', pattern_id)} - 검증 프레임워크

### 협업 검증 체크리스트
"""
        
        content += yaml.dump(val_framework, allow_unicode=True, default_flow_style=False)
        
        metadata = {
            "chunk_id": f"{pattern_id}_validation",
            "chunk_type": "validation_framework",
            "agent": "explorer",
            "pattern_id": pattern_id,
            "pattern_type": "business_model",
            "section": "validation",
            
            # 검증 필요 에이전트 태그
            "validation_agents": ["quantifier", "validator", "observer"],
            
            "source_file": "umis_business_model_patterns.yaml",
            "token_count": len(content.split()),
        }
        
        return {
            "content": content.strip(),
            "metadata": metadata
        }
    
    def _create_case_chunks(
        self, 
        pattern_id: str, 
        pattern: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        성공 사례들을 각각 독립 청크로 생성
        
        왜 사례별로 분할?
        - Explorer가 "유사한 산업 사례" 검색 시
        - 특정 사례만 정확하게 검색 가능
        - 예: "음식 배달" 검색 → "배달의민족" 청크만 매칭
        """
        cases_lib = pattern["success_case_library"]
        chunks = []
        
        for region in ["domestic", "global"]:
            if region not in cases_lib:
                continue
            
            cases = cases_lib[region]
            for company_name, case_data in cases.items():
                content = f"""
## 성공 사례: {company_name}

**패턴**: {pattern.get('concept', {}).get('name', pattern_id)}
**지역**: {region}

"""
                
                # 사례 데이터를 YAML로 직렬화
                content += yaml.dump(case_data, allow_unicode=True, default_flow_style=False)
                
                # 핵심 성공 요인 추출
                csf = case_data.get("critical_success_factors", [])
                
                metadata = {
                    "chunk_id": f"{pattern_id}_case_{company_name}",
                    "chunk_type": "success_case",
                    "agent": "explorer",
                    "pattern_id": pattern_id,
                    "pattern_type": "business_model",
                    "section": "case_study",
                    
                    # 사례 특화 메타데이터
                    "company": company_name,
                    "region": region,
                    "industry": case_data.get("market", "unknown"),
                    "critical_success_factors": csf if isinstance(csf, list) else [],
                    
                    "source_file": "umis_business_model_patterns.yaml",
                    "token_count": len(content.split()),
                }
                
                chunks.append({
                    "content": content.strip(),
                    "metadata": metadata
                })
        
        return chunks
    
    def convert_disruption_patterns_for_explorer(self) -> List[Dict[str, Any]]:
        """
        Disruption 패턴을 Explorer 관점으로 청킹
        
        Explorer의 관심사 (Disruption 특화):
        - 1등의 어떤 약점을 공략하나?
        - Counter-Positioning 메커니즘은?
        - 1등이 못 따라오는 이유는?
        - 실제 추월 사례는?
        
        청킹 전략:
        - 1개 패턴 = 여러 청크
        - 사례별로 상세 청킹 (사례가 매우 중요!)
        """
        logger.info("🔥 Disruption 패턴 → Explorer 청크 변환 시작")
        
        data = self.load_yaml("umis_disruption_patterns.yaml")
        chunks = []
        
        # 5개 Disruption 패턴
        pattern_ids = [
            "innovation_disruption",
            "low_end_disruption",
            "channel_disruption",
            "experience_disruption",
            "continuous_innovation_disruption"
        ]
        
        for pattern_id in track(pattern_ids, description="Disruption 패턴 처리 중..."):
            if pattern_id not in data:
                logger.warning(f"  ⚠️  패턴 없음: {pattern_id}")
                continue
            
            pattern = data[pattern_id]
            
            # 청크 1: 패턴 개요 + Incumbent Dilemma
            chunks.append(self._create_disruption_overview_chunk(pattern_id, pattern))
            
            # 청크 2: Attacker Strategy
            if "attacker_strategy" in pattern:
                chunks.append(self._create_attacker_strategy_chunk(pattern_id, pattern))
            
            # 청크 3: Validation Framework
            if "validation_framework" in pattern:
                chunks.append(self._create_disruption_validation_chunk(pattern_id, pattern))
            
            # 청크 4-N: 성공 사례들 (Disruption은 사례가 핵심!)
            if "success_case_library" in pattern:
                chunks.extend(self._create_disruption_case_chunks(pattern_id, pattern))
        
        logger.info(f"  ✅ 총 {len(chunks)}개 Disruption 청크 생성")
        return chunks
    
    def _create_disruption_overview_chunk(
        self, 
        pattern_id: str, 
        pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Disruption 패턴 개요 청크
        
        핵심: Incumbent Dilemma (1등의 딜레마)
        """
        concept = pattern.get("concept", {})
        triggers = pattern.get("trigger_observations", {})
        incumbent_dilemma = pattern.get("incumbent_dilemma", {})
        
        content = f"""
## {concept.get('name', pattern_id)}

### 핵심 개념
- **본질**: {concept.get('essence', 'N/A')}
- **태그라인**: {concept.get('tagline', 'N/A')}

### 트리거 시그널 (1등의 약점 포착)
"""
        
        # 트리거 추가
        if "incumbent_signals" in triggers:
            inc_signals = triggers["incumbent_signals"]
            for category, signals_list in inc_signals.items():
                content += f"\n**{category}**:\n"
                if isinstance(signals_list, list):
                    for signal in signals_list:
                        content += f"- {signal}\n"
                elif isinstance(signals_list, dict):
                    for key, value in signals_list.items():
                        if isinstance(value, list):
                            content += f"- {key}:\n"
                            for v in value:
                                content += f"  - {v}\n"
        
        # Incumbent Dilemma (핵심!)
        content += "\n### 1등의 딜레마 (왜 못 따라오나?)\n"
        if "why_they_cant_follow" in incumbent_dilemma:
            content += yaml.dump(
                incumbent_dilemma["why_they_cant_follow"], 
                allow_unicode=True, 
                default_flow_style=False
            )
        
        metadata = {
            "chunk_id": f"{pattern_id}_overview",
            "chunk_type": "disruption_overview",
            "agent": "explorer",
            "pattern_id": pattern_id,
            "pattern_type": "disruption",
            "section": "concept_and_dilemma",
            
            "keywords": self._extract_keywords(concept),
            "source_file": "umis_disruption_patterns.yaml",
            "token_count": len(content.split()),
        }
        
        return {
            "content": content.strip(),
            "metadata": metadata
        }
    
    def _create_attacker_strategy_chunk(
        self, 
        pattern_id: str, 
        pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Attacker 전략 청크 (어떻게 공략하나?)"""
        strategy = pattern["attacker_strategy"]
        
        content = f"""
## {pattern.get('concept', {}).get('name', pattern_id)} - Attacker 전략

### 실행 방법
"""
        content += yaml.dump(strategy, allow_unicode=True, default_flow_style=False)
        
        metadata = {
            "chunk_id": f"{pattern_id}_strategy",
            "chunk_type": "attacker_strategy",
            "agent": "explorer",
            "pattern_id": pattern_id,
            "pattern_type": "disruption",
            "section": "strategy",
            "source_file": "umis_disruption_patterns.yaml",
            "token_count": len(content.split()),
        }
        
        return {
            "content": content.strip(),
            "metadata": metadata
        }
    
    def _create_disruption_validation_chunk(
        self, 
        pattern_id: str, 
        pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Disruption 검증 프레임워크 (Counter-Positioning 테스트!)"""
        val_framework = pattern["validation_framework"]
        
        content = f"""
## {pattern.get('concept', {}).get('name', pattern_id)} - 검증 프레임워크

### Counter-Positioning 테스트
- 우리 전략을 1등이 모방하면?
- 1등에게 발생할 손해는?
- 손해 > 이익인가?

### 검증 체크리스트
"""
        content += yaml.dump(val_framework, allow_unicode=True, default_flow_style=False)
        
        metadata = {
            "chunk_id": f"{pattern_id}_validation",
            "chunk_type": "disruption_validation",
            "agent": "explorer",
            "pattern_id": pattern_id,
            "pattern_type": "disruption",
            "section": "validation",
            "validation_agents": ["observer", "quantifier", "validator"],
            "source_file": "umis_disruption_patterns.yaml",
            "token_count": len(content.split()),
        }
        
        return {
            "content": content.strip(),
            "metadata": metadata
        }
    
    def _create_disruption_case_chunks(
        self, 
        pattern_id: str, 
        pattern: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Disruption 사례 청크들
        
        중요: Disruption은 사례가 매우 상세함!
        - Incumbent vs Attacker 구조
        - Counter-Positioning 메커니즘
        - Timeline
        - 실제 결과
        
        → 각 사례를 2-3개 청크로 분할
        """
        cases_lib = pattern.get("success_case_library", {})
        chunks = []
        
        for case_id, case_data in cases_lib.items():
            if case_id.startswith("case_"):
                # 메인 사례 청크
                chunks.append(self._create_single_disruption_case(
                    pattern_id, 
                    case_id, 
                    case_data
                ))
        
        return chunks
    
    def _create_single_disruption_case(
        self, 
        pattern_id: str, 
        case_id: str, 
        case_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """단일 Disruption 사례 청크"""
        content = f"""
## Disruption 사례: {case_id}

**패턴**: {pattern_id}
**시장**: {case_data.get('market', 'N/A')}
**기간**: {case_data.get('period', 'N/A')}
**결과**: {case_data.get('outcome', 'N/A')}

### Counter-Positioning 메커니즘
"""
        
        # Counter-Positioning 메커니즘 (핵심!)
        if "counter_positioning_mechanism" in case_data:
            content += yaml.dump(
                case_data["counter_positioning_mechanism"], 
                allow_unicode=True, 
                default_flow_style=False
            )
        
        # Timeline
        if "disruption_timeline" in case_data:
            content += "\n### Disruption Timeline\n"
            content += yaml.dump(
                case_data["disruption_timeline"], 
                allow_unicode=True, 
                default_flow_style=False
            )
        
        # Key Metrics
        if "key_metrics" in case_data:
            content += "\n### 주요 지표\n"
            content += yaml.dump(
                case_data["key_metrics"], 
                allow_unicode=True, 
                default_flow_style=False
            )
        
        # CSF
        csf = case_data.get("critical_success_factors", [])
        if csf:
            content += "\n### 핵심 성공 요인\n"
            for factor in csf:
                content += f"- {factor}\n"
        
        metadata = {
            "chunk_id": f"{pattern_id}_{case_id}",
            "chunk_type": "disruption_case",
            "agent": "explorer",
            "pattern_id": pattern_id,
            "pattern_type": "disruption",
            "section": "case_study",
            
            # 사례 메타데이터
            "case_id": case_id,
            "market": case_data.get("market", "unknown"),
            "period": case_data.get("period", "unknown"),
            "outcome": case_data.get("outcome", "unknown"),
            "critical_success_factors": csf if isinstance(csf, list) else [],
            
            "source_file": "umis_disruption_patterns.yaml",
            "token_count": len(content.split()),
        }
        
        return {
            "content": content.strip(),
            "metadata": metadata
        }
    
    def _extract_keywords(self, concept: Dict[str, Any]) -> List[str]:
        """
        컨셉에서 검색 키워드 추출
        
        간단한 방법: essence와 core_value에서 주요 단어 추출
        향후 개선: LLM으로 자동 키워드 추출
        """
        keywords = []
        
        essence = concept.get("essence", "")
        core_value = concept.get("core_value", "")
        
        # 단순 단어 분할 (향후 형태소 분석으로 개선 가능)
        text = f"{essence} {core_value}"
        words = text.replace(",", " ").split()
        
        # 2글자 이상 단어만
        keywords = [w.strip() for w in words if len(w.strip()) >= 2]
        
        return keywords[:10]  # 최대 10개
    
    def save_chunks(self, chunks: List[Dict[str, Any]], filename: str) -> None:
        """
        청크를 JSON Lines 형식으로 저장
        
        JSON Lines (.jsonl) 형식:
        - 한 줄에 하나의 JSON 객체
        - 스트리밍 처리 가능
        - 대용량 데이터에 효율적
        
        예시:
        {"content": "...", "metadata": {...}}
        {"content": "...", "metadata": {...}}
        {"content": "...", "metadata": {...}}
        """
        filepath = self.chunks_dir / filename
        logger.info(f"💾 청크 저장 중: {filepath}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            for chunk in chunks:
                # 한 줄에 하나의 JSON
                json.dump(chunk, f, ensure_ascii=False)
                f.write('\n')
        
        # 통계 출력
        total_tokens = sum(c["metadata"]["token_count"] for c in chunks)
        logger.info(f"  ✅ {len(chunks)}개 청크 저장 완료")
        logger.info(f"  📊 총 토큰 수: ~{total_tokens:,}")
        logger.info(f"  📍 파일 크기: {filepath.stat().st_size / 1024:.1f} KB")


def main():
    """메인 실행 함수"""
    console.print("\n[bold blue]🚀 UMIS YAML → RAG Chunks 변환[/bold blue]\n")
    
    # 프로젝트 루트 기준 경로
    data_dir = project_root / "data"
    
    # 컨버터 초기화
    converter = UMISYAMLConverter(data_dir)
    
    # Phase 1: 비즈니스 모델 패턴 → Explorer 청크
    console.print("[yellow]📊 Phase 1: 비즈니스 모델 패턴 변환[/yellow]")
    explorer_bm_chunks = converter.convert_business_model_patterns_for_explorer()
    converter.save_chunks(explorer_bm_chunks, "explorer_business_models.jsonl")
    
    # Phase 2: Disruption 패턴 → Explorer 청크
    console.print("\n[yellow]🔥 Phase 2: Disruption 패턴 변환[/yellow]")
    explorer_dp_chunks = converter.convert_disruption_patterns_for_explorer()
    converter.save_chunks(explorer_dp_chunks, "explorer_disruption_patterns.jsonl")
    
    # TODO: Phase 3: Observer 관점 청크 (향후)
    # TODO: Phase 4: Quantifier 관점 청크 (향후)
    
    console.print("\n[bold green]✅ 변환 완료![/bold green]\n")
    console.print(f"출력 디렉토리: {converter.chunks_dir}")
    console.print("\n다음 단계:")
    console.print("  python scripts/02_build_index.py --agent explorer")


if __name__ == "__main__":
    main()

