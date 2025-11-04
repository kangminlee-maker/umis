"""
Builder Contract
각 Builder가 반환하는 계약 (생성한 Named Range 목록)

목적:
  - Builder 간 결합도 감소
  - 구조 독립성 확보
  - 자동 검증 가능

사용:
  contract = builder.create_sheet(...)
  named_ranges = contract.named_ranges
  next_builder.create_sheet(..., prev_contract=contract)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class ValidationStatus(Enum):
    """검증 상태"""
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ValidationResult:
    """
    개별 검증 결과
    
    Attributes:
        check_name: 검증 항목 이름
        status: 검증 상태
        message: 결과 메시지
        details: 추가 세부 정보
    """
    check_name: str
    status: ValidationStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    
    def __repr__(self) -> str:
        return f"ValidationResult({self.check_name}: {self.status.value})"


@dataclass
class BuilderContract:
    """
    Builder가 반환하는 계약
    
    Attributes:
        sheet_name: 생성한 시트 이름
        named_ranges: {range_name: cell_address}
        row_numbers: {key: row_number} (옵션, 레거시 호환용)
        metadata: 추가 정보 (세그먼트 수, 년도 수 등)
        validation_results: Inline Validation 결과 목록 (v7.2.0)
    """
    
    sheet_name: str
    named_ranges: Dict[str, str] = field(default_factory=dict)
    row_numbers: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    validation_results: List[ValidationResult] = field(default_factory=list)
    
    def add_named_range(self, name: str, address: str) -> None:
        """
        Named Range 추가
        
        Args:
            name: Named Range 이름 (예: 'Revenue_Y0')
            address: 셀 주소 (예: 'Revenue_Buildup!B9')
        """
        self.named_ranges[name] = address
    
    def add_row_number(self, key: str, row: int) -> None:
        """
        행 번호 추가 (레거시 호환용)
        
        Args:
            key: 키 (예: 'total_revenue_row')
            row: 행 번호
        """
        self.row_numbers[key] = row
    
    def add_metadata(self, key: str, value: Any) -> None:
        """
        메타데이터 추가
        
        Args:
            key: 키 (예: 'num_segments', 'years')
            value: 값
        """
        self.metadata[key] = value
    
    def get_named_range(self, name: str) -> Optional[str]:
        """
        Named Range 조회
        
        Args:
            name: Named Range 이름
        
        Returns:
            셀 주소 또는 None
        """
        return self.named_ranges.get(name)
    
    def get_row_number(self, key: str) -> Optional[int]:
        """
        행 번호 조회
        
        Args:
            key: 키
        
        Returns:
            행 번호 또는 None
        """
        return self.row_numbers.get(key)
    
    def get_metadata(self, key: str) -> Optional[Any]:
        """
        메타데이터 조회
        
        Args:
            key: 키
        
        Returns:
            값 또는 None
        """
        return self.metadata.get(key)
    
    def has_named_range(self, name: str) -> bool:
        """
        Named Range 존재 여부
        
        Args:
            name: Named Range 이름
        
        Returns:
            존재 여부
        """
        return name in self.named_ranges
    
    def list_named_ranges(self) -> List[str]:
        """
        모든 Named Range 목록
        
        Returns:
            Named Range 이름 목록
        """
        return list(self.named_ranges.keys())
    
    def add_validation_result(self, result: ValidationResult) -> None:
        """
        검증 결과 추가
        
        Args:
            result: ValidationResult
        """
        self.validation_results.append(result)
    
    def add_validation(
        self,
        check_name: str,
        status: ValidationStatus,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        검증 결과 추가 (간편 버전)
        
        Args:
            check_name: 검증 항목 이름
            status: 검증 상태
            message: 결과 메시지
            details: 추가 세부 정보
        """
        result = ValidationResult(
            check_name=check_name,
            status=status,
            message=message,
            details=details or {}
        )
        self.add_validation_result(result)
    
    def has_failures(self) -> bool:
        """
        검증 실패 여부
        
        Returns:
            실패 항목이 있으면 True
        """
        return any(r.status == ValidationStatus.FAILED for r in self.validation_results)
    
    def has_warnings(self) -> bool:
        """
        경고 여부
        
        Returns:
            경고 항목이 있으면 True
        """
        return any(r.status == ValidationStatus.WARNING for r in self.validation_results)
    
    def validation_summary(self) -> str:
        """
        검증 결과 요약
        
        Returns:
            요약 문자열
        """
        if not self.validation_results:
            return "No validation results"
        
        passed = sum(1 for r in self.validation_results if r.status == ValidationStatus.PASSED)
        warnings = sum(1 for r in self.validation_results if r.status == ValidationStatus.WARNING)
        failed = sum(1 for r in self.validation_results if r.status == ValidationStatus.FAILED)
        skipped = sum(1 for r in self.validation_results if r.status == ValidationStatus.SKIPPED)
        
        lines = [
            f"Validation Summary:",
            f"  ✅ Passed: {passed}",
            f"  ⚠️  Warnings: {warnings}",
            f"  ❌ Failed: {failed}",
            f"  ⏭️  Skipped: {skipped}"
        ]
        
        if failed > 0:
            lines.append("\n  Failed checks:")
            for result in self.validation_results:
                if result.status == ValidationStatus.FAILED:
                    lines.append(f"    - {result.check_name}: {result.message}")
        
        if warnings > 0:
            lines.append("\n  Warnings:")
            for result in self.validation_results:
                if result.status == ValidationStatus.WARNING:
                    lines.append(f"    - {result.check_name}: {result.message}")
        
        return "\n".join(lines)
    
    def summary(self) -> str:
        """
        계약 요약
        
        Returns:
            요약 문자열
        """
        lines = [
            f"BuilderContract: {self.sheet_name}",
            f"  Named Ranges: {len(self.named_ranges)}",
            f"  Row Numbers: {len(self.row_numbers)}",
            f"  Metadata: {len(self.metadata)}",
            f"  Validations: {len(self.validation_results)}"
        ]
        
        if self.named_ranges:
            lines.append("  Named Ranges List:")
            for name in sorted(self.named_ranges.keys())[:10]:  # 최대 10개만
                lines.append(f"    - {name}")
            if len(self.named_ranges) > 10:
                lines.append(f"    ... and {len(self.named_ranges) - 10} more")
        
        if self.validation_results:
            lines.append("\n  " + self.validation_summary())
        
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        return f"BuilderContract(sheet={self.sheet_name}, ranges={len(self.named_ranges)})"


@dataclass
class ContractRegistry:
    """
    여러 Builder Contract를 관리하는 레지스트리
    
    Generator가 사용하여 모든 Builder의 Contract를 추적
    """
    
    contracts: Dict[str, BuilderContract] = field(default_factory=dict)
    
    def register(self, contract: BuilderContract) -> None:
        """
        Contract 등록
        
        Args:
            contract: Builder Contract
        """
        self.contracts[contract.sheet_name] = contract
    
    def get(self, sheet_name: str) -> Optional[BuilderContract]:
        """
        Contract 조회
        
        Args:
            sheet_name: 시트 이름
        
        Returns:
            BuilderContract 또는 None
        """
        return self.contracts.get(sheet_name)
    
    def find_named_range(self, range_name: str) -> Optional[BuilderContract]:
        """
        Named Range를 가진 Contract 찾기
        
        Args:
            range_name: Named Range 이름
        
        Returns:
            BuilderContract 또는 None
        """
        for contract in self.contracts.values():
            if contract.has_named_range(range_name):
                return contract
        return None
    
    def list_all_named_ranges(self) -> List[str]:
        """
        모든 Named Range 목록
        
        Returns:
            Named Range 이름 목록
        """
        all_ranges = []
        for contract in self.contracts.values():
            all_ranges.extend(contract.list_named_ranges())
        return all_ranges
    
    def summary(self) -> str:
        """
        전체 요약
        
        Returns:
            요약 문자열
        """
        lines = [
            f"ContractRegistry: {len(self.contracts)} contracts",
            f"Total Named Ranges: {len(self.list_all_named_ranges())}"
        ]
        
        for contract in self.contracts.values():
            lines.append(f"\n{contract.summary()}")
        
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        return f"ContractRegistry(contracts={len(self.contracts)})"

