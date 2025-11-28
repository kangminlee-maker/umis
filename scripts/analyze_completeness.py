#!/usr/bin/env python3
"""
UMIS Code Completeness Analyzer

코드 구현 완성도를 종합적으로 분석합니다.

분석 영역:
1. Stub Detection: 스텁 탐지 (empty functions, NotImplementedError)
2. Implementation Completeness: 구현 완성도 (abstract methods, interface gaps)
3. Technical Debt: 기술 부채 (TODO/FIXME, workarounds)
4. Dead Code: 데드 코드 (unused functions, unreachable code)

Usage:
    python3 scripts/analyze_completeness.py
    python3 scripts/analyze_completeness.py --category stub
    python3 scripts/analyze_completeness.py --detailed
"""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
import json
import re
import argparse


@dataclass
class CodeIssue:
    """코드 이슈 기본 클래스"""
    file_path: str
    line_number: int
    category: str  # stub, completeness, debt, dead_code
    subcategory: str
    severity: str  # critical, high, medium, low
    description: str
    code_snippet: str = ""
    suggestion: str = ""


@dataclass
class FunctionInfo:
    """함수 정보"""
    name: str
    file_path: str
    line_number: int
    is_async: bool = False
    is_abstract: bool = False
    has_body: bool = True
    body_type: str = "implemented"  # implemented, pass, notimplemented, docstring_only
    decorators: List[str] = field(default_factory=list)
    parameters: List[str] = field(default_factory=list)
    returns: Optional[str] = None
    docstring: Optional[str] = None
    called_by: Set[str] = field(default_factory=set)
    calls: Set[str] = field(default_factory=set)


@dataclass
class ClassInfo:
    """클래스 정보"""
    name: str
    file_path: str
    line_number: int
    base_classes: List[str] = field(default_factory=list)
    methods: Dict[str, FunctionInfo] = field(default_factory=dict)
    abstract_methods: Set[str] = field(default_factory=set)
    is_abstract: bool = False


class CompletenessAnalyzer:
    """코드 완성도 종합 분석기"""
    
    def __init__(self, root_dir: Path, package_name: str = "umis_rag"):
        self.root_dir = root_dir
        self.package_name = package_name
        self.issues: List[CodeIssue] = []
        self.functions: Dict[str, FunctionInfo] = {}
        self.classes: Dict[str, ClassInfo] = {}
        self.call_graph: Dict[str, Set[str]] = defaultdict(set)
        
    def analyze(self) -> None:
        """전체 분석 실행"""
        print("=" * 80)
        print("  UMIS Code Completeness Analyzer")
        print("=" * 80)
        
        package_dir = self.root_dir / self.package_name
        if not package_dir.exists():
            raise FileNotFoundError(f"Package not found: {package_dir}")
        
        python_files = list(package_dir.rglob("*.py"))
        print(f"\n📁 Found {len(python_files)} Python files")
        
        # Phase 1: AST 파싱 및 정보 수집
        print("\n🔍 Phase 1: Parsing AST and collecting information...")
        for py_file in python_files:
            self._parse_file(py_file)
        
        print(f"   ✅ Parsed {len(self.functions)} functions")
        print(f"   ✅ Parsed {len(self.classes)} classes")
        
        # Phase 2: 문제 탐지
        print("\n🔍 Phase 2: Detecting issues...")
        self._detect_stub_issues()
        self._detect_completeness_issues()
        self._detect_technical_debt()
        self._detect_dead_code()
        
        print(f"\n   ✅ Found {len(self.issues)} total issues")
    
    def _parse_file(self, file_path: Path) -> None:
        """단일 파일 파싱"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content, filename=str(file_path))
            
            visitor = ASTVisitor(str(file_path), self)
            visitor.visit(tree)
            
        except SyntaxError as e:
            self.issues.append(CodeIssue(
                file_path=str(file_path),
                line_number=e.lineno or 0,
                category="parsing",
                subcategory="syntax_error",
                severity="critical",
                description=f"Syntax error: {e.msg}"
            ))
        except Exception as e:
            print(f"   ⚠️  Error parsing {file_path}: {e}")
    
    # ========================================
    # 1. STUB DETECTION
    # ========================================
    
    def _detect_stub_issues(self) -> None:
        """스텁 탐지"""
        print("   → Detecting stubs...")
        
        for func_name, func_info in self.functions.items():
            # 1-1. Empty Functions (pass only)
            if func_info.body_type == "pass":
                self.issues.append(CodeIssue(
                    file_path=func_info.file_path,
                    line_number=func_info.line_number,
                    category="stub",
                    subcategory="empty_function",
                    severity="high",
                    description=f"Empty function with only 'pass': {func_info.name}",
                    suggestion="Implement the function or add NotImplementedError"
                ))
            
            # 1-2. NotImplementedError
            elif func_info.body_type == "notimplemented":
                self.issues.append(CodeIssue(
                    file_path=func_info.file_path,
                    line_number=func_info.line_number,
                    category="stub",
                    subcategory="not_implemented",
                    severity="high",
                    description=f"Function raises NotImplementedError: {func_info.name}",
                    suggestion="Implement the function"
                ))
            
            # 1-3. Docstring Only
            elif func_info.body_type == "docstring_only":
                self.issues.append(CodeIssue(
                    file_path=func_info.file_path,
                    line_number=func_info.line_number,
                    category="stub",
                    subcategory="docstring_only",
                    severity="medium",
                    description=f"Function has only docstring: {func_info.name}",
                    suggestion="Add implementation"
                ))
    
    # ========================================
    # 2. IMPLEMENTATION COMPLETENESS
    # ========================================
    
    def _detect_completeness_issues(self) -> None:
        """구현 완성도 분석"""
        print("   → Checking implementation completeness...")
        
        # 2-1. Abstract Methods Not Implemented
        for class_name, class_info in self.classes.items():
            if class_info.is_abstract:
                continue  # Abstract class 자체는 OK
            
            # 부모 클래스의 abstract methods 확인
            for base_class in class_info.base_classes:
                if base_class in self.classes:
                    base_info = self.classes[base_class]
                    for abstract_method in base_info.abstract_methods:
                        if abstract_method not in class_info.methods:
                            self.issues.append(CodeIssue(
                                file_path=class_info.file_path,
                                line_number=class_info.line_number,
                                category="completeness",
                                subcategory="unimplemented_abstract",
                                severity="critical",
                                description=f"Class {class_name} does not implement abstract method '{abstract_method}' from {base_class}",
                                suggestion=f"Implement {abstract_method} method"
                            ))
        
        # 2-2. Mock/Placeholder Returns
        # (이것은 AST만으로는 어려워서 휴리스틱 사용)
        for func_name, func_info in self.functions.items():
            if func_info.docstring and any(keyword in func_info.docstring.lower() 
                                          for keyword in ["todo", "placeholder", "mock", "temporary"]):
                self.issues.append(CodeIssue(
                    file_path=func_info.file_path,
                    line_number=func_info.line_number,
                    category="completeness",
                    subcategory="placeholder",
                    severity="medium",
                    description=f"Function has placeholder/mock indicator in docstring: {func_info.name}",
                    suggestion="Complete the implementation"
                ))
    
    # ========================================
    # 3. TECHNICAL DEBT
    # ========================================
    
    def _detect_technical_debt(self) -> None:
        """기술 부채 탐지"""
        print("   → Scanning for technical debt...")
        
        # 3-1. TODO/FIXME Comments
        package_dir = self.root_dir / self.package_name
        for py_file in package_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for i, line in enumerate(lines, 1):
                    # TODO/FIXME/XXX/HACK 탐지
                    if re.search(r'#\s*(TODO|FIXME|XXX|HACK|WIP|TEMP)', line, re.IGNORECASE):
                        match = re.search(r'#\s*(TODO|FIXME|XXX|HACK|WIP|TEMP)[:\s]*(.*)', line, re.IGNORECASE)
                        if match:
                            marker = match.group(1).upper()
                            comment = match.group(2).strip()
                            
                            severity_map = {
                                "FIXME": "high",
                                "TODO": "medium",
                                "XXX": "high",
                                "HACK": "high",
                                "WIP": "medium",
                                "TEMP": "high"
                            }
                            
                            self.issues.append(CodeIssue(
                                file_path=str(py_file),
                                line_number=i,
                                category="debt",
                                subcategory=marker.lower(),
                                severity=severity_map.get(marker, "medium"),
                                description=f"{marker}: {comment or '(no description)'}",
                                code_snippet=line.strip(),
                                suggestion="Address the technical debt"
                            ))
            except Exception as e:
                print(f"   ⚠️  Error scanning {py_file}: {e}")
    
    # ========================================
    # 4. DEAD CODE
    # ========================================
    
    def _detect_dead_code(self) -> None:
        """데드 코드 탐지"""
        print("   → Detecting dead code...")
        
        # 4-1. Unused Functions (Call Graph 기반)
        # Entry points 제외 (main, __init__, etc.)
        entry_point_patterns = ['main', '__init__', '__main__', 'run', 'execute', 'start']
        
        for func_name, func_info in self.functions.items():
            # Entry point는 제외
            if any(pattern in func_info.name for pattern in entry_point_patterns):
                continue
            
            # Private/magic 메서드는 제외
            if func_info.name.startswith('_') and not func_info.name.startswith('__'):
                continue
            
            # 호출되지 않는 함수
            if len(func_info.called_by) == 0:
                # 단, public API일 수 있으므로 severity는 low
                self.issues.append(CodeIssue(
                    file_path=func_info.file_path,
                    line_number=func_info.line_number,
                    category="dead_code",
                    subcategory="unused_function",
                    severity="low",
                    description=f"Function appears unused: {func_info.name}",
                    suggestion="Remove if truly unused, or export as public API"
                ))
    
    def generate_report(self) -> Dict:
        """리포트 생성"""
        print("\n📊 Generating completeness report...")
        
        # 카테고리별 집계
        by_category = defaultdict(list)
        by_severity = defaultdict(list)
        by_file = defaultdict(list)
        
        for issue in self.issues:
            by_category[issue.category].append(issue)
            by_severity[issue.severity].append(issue)
            # 파일 경로를 상대 경로로 변환
            rel_path = str(Path(issue.file_path).relative_to(self.root_dir))
            by_file[rel_path].append(issue)
        
        report = {
            "summary": {
                "total_issues": len(self.issues),
                "by_category": {cat: len(issues) for cat, issues in by_category.items()},
                "by_severity": {sev: len(issues) for sev, issues in by_severity.items()},
                "total_functions": len(self.functions),
                "total_classes": len(self.classes)
            },
            "issues": [],
            "top_files": []
        }
        
        # 이슈 상세
        for issue in self.issues:
            rel_path = str(Path(issue.file_path).relative_to(self.root_dir))
            report["issues"].append({
                "file": rel_path,
                "line": issue.line_number,
                "category": issue.category,
                "subcategory": issue.subcategory,
                "severity": issue.severity,
                "description": issue.description,
                "suggestion": issue.suggestion
            })
        
        # Top files (가장 많은 이슈)
        sorted_files = sorted(by_file.items(), key=lambda x: len(x[1]), reverse=True)
        report["top_files"] = [
            {"file": file, "issue_count": len(issues)}
            for file, issues in sorted_files[:20]
        ]
        
        return report
    
    def print_summary(self) -> None:
        """요약 출력"""
        by_category = defaultdict(int)
        by_severity = defaultdict(int)
        
        for issue in self.issues:
            by_category[issue.category] += 1
            by_severity[issue.severity] += 1
        
        print("\n" + "=" * 80)
        print("  Summary")
        print("=" * 80)
        
        print(f"\n📊 Total Issues: {len(self.issues)}")
        
        print("\n📁 By Category:")
        category_names = {
            "stub": "Stub Detection",
            "completeness": "Implementation Completeness",
            "debt": "Technical Debt",
            "dead_code": "Dead Code"
        }
        for cat, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
            print(f"   {category_names.get(cat, cat):30} {count:>4}")
        
        print("\n⚠️  By Severity:")
        severity_order = ["critical", "high", "medium", "low"]
        for sev in severity_order:
            if sev in by_severity:
                print(f"   {sev.capitalize():30} {by_severity[sev]:>4}")
    
    def save_report(self, output_path: Path) -> None:
        """리포트 저장"""
        report = self.generate_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Report saved to: {output_path}")


class ASTVisitor(ast.NodeVisitor):
    """AST 방문자"""
    
    def __init__(self, file_path: str, analyzer: CompletenessAnalyzer):
        self.file_path = file_path
        self.analyzer = analyzer
        self.current_class: Optional[str] = None
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """클래스 정의 방문"""
        class_name = node.name
        qualified_name = f"{self.file_path}::{class_name}"
        
        # Base classes
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(base.attr)
        
        # Abstract 여부 확인
        is_abstract = any(
            isinstance(dec, ast.Name) and dec.id in ['ABC', 'ABCMeta']
            for dec in node.decorator_list
        ) or 'ABC' in base_classes
        
        class_info = ClassInfo(
            name=class_name,
            file_path=self.file_path,
            line_number=node.lineno,
            base_classes=base_classes,
            is_abstract=is_abstract
        )
        
        self.analyzer.classes[qualified_name] = class_info
        
        # 메서드 분석
        old_class = self.current_class
        self.current_class = qualified_name
        self.generic_visit(node)
        self.current_class = old_class
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """함수 정의 방문"""
        self._process_function(node, is_async=False)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """비동기 함수 정의 방문"""
        self._process_function(node, is_async=True)
    
    def _process_function(self, node, is_async: bool) -> None:
        """함수 처리"""
        func_name = node.name
        
        # Decorators
        decorators = []
        is_abstract = False
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                decorators.append(dec.id)
                if dec.id in ['abstractmethod', 'abc.abstractmethod']:
                    is_abstract = True
        
        # Parameters
        parameters = [arg.arg for arg in node.args.args]
        
        # Docstring
        docstring = ast.get_docstring(node)
        
        # Body type 분석
        body_type, has_body = self._analyze_body(node.body, docstring)
        
        # Function info 생성
        qualified_name = f"{self.file_path}::{self.current_class or 'module'}::{func_name}"
        
        func_info = FunctionInfo(
            name=func_name,
            file_path=self.file_path,
            line_number=node.lineno,
            is_async=is_async,
            is_abstract=is_abstract,
            has_body=has_body,
            body_type=body_type,
            decorators=decorators,
            parameters=parameters,
            docstring=docstring
        )
        
        self.analyzer.functions[qualified_name] = func_info
        
        # 클래스 메서드라면 클래스에 추가
        if self.current_class:
            class_info = self.analyzer.classes[self.current_class]
            class_info.methods[func_name] = func_info
            if is_abstract:
                class_info.abstract_methods.add(func_name)
        
        # Call graph 구축 (간단 버전)
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    called_func = child.func.id
                    func_info.calls.add(called_func)
    
    def _analyze_body(self, body: List[ast.stmt], docstring: Optional[str]) -> Tuple[str, bool]:
        """함수 본문 분석"""
        # Docstring 제외한 실제 body
        real_body = body
        if docstring:
            real_body = body[1:] if len(body) > 1 else []
        
        if not real_body:
            if docstring:
                return "docstring_only", False
            return "pass", False
        
        # Pass만 있는 경우
        if len(real_body) == 1 and isinstance(real_body[0], ast.Pass):
            return "pass", False
        
        # NotImplementedError
        if len(real_body) == 1 and isinstance(real_body[0], ast.Raise):
            if isinstance(real_body[0].exc, ast.Call):
                if isinstance(real_body[0].exc.func, ast.Name):
                    if real_body[0].exc.func.id == "NotImplementedError":
                        return "notimplemented", False
        
        # Ellipsis (...)
        if len(real_body) == 1 and isinstance(real_body[0], ast.Expr):
            if isinstance(real_body[0].value, ast.Constant) and real_body[0].value.value == ...:
                return "pass", False
        
        return "implemented", True


def main():
    parser = argparse.ArgumentParser(description="UMIS Code Completeness Analyzer")
    parser.add_argument("--category", choices=["stub", "completeness", "debt", "dead_code"], 
                       help="Analyze specific category only")
    parser.add_argument("--severity", choices=["critical", "high", "medium", "low"],
                       help="Filter by severity")
    parser.add_argument("--output-dir", type=str, default="dev_docs",
                       help="Output directory")
    parser.add_argument("--detailed", action="store_true",
                       help="Show detailed issue list")
    
    args = parser.parse_args()
    
    # Root directory
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    
    # 분석기 초기화
    analyzer = CompletenessAnalyzer(root_dir=root_dir, package_name="umis_rag")
    
    # 분석 실행
    analyzer.analyze()
    
    # 필터링
    if args.category:
        analyzer.issues = [i for i in analyzer.issues if i.category == args.category]
    if args.severity:
        analyzer.issues = [i for i in analyzer.issues if i.severity == args.severity]
    
    # 요약 출력
    analyzer.print_summary()
    
    # 상세 출력
    if args.detailed and analyzer.issues:
        print("\n" + "=" * 80)
        print("  Detailed Issues")
        print("=" * 80)
        
        by_category = defaultdict(list)
        for issue in analyzer.issues:
            by_category[issue.category].append(issue)
        
        for category, issues in sorted(by_category.items()):
            print(f"\n### {category.upper()}")
            for issue in issues[:20]:  # 상위 20개만
                rel_path = str(Path(issue.file_path).relative_to(root_dir))
                print(f"\n  📍 {rel_path}:{issue.line_number}")
                print(f"     [{issue.severity.upper()}] {issue.subcategory}")
                print(f"     {issue.description}")
                if issue.suggestion:
                    print(f"     💡 {issue.suggestion}")
    
    # 리포트 저장
    output_dir = root_dir / args.output_dir
    output_dir.mkdir(exist_ok=True)
    
    report_path = output_dir / "completeness_analysis.json"
    analyzer.save_report(report_path)
    
    print("\n" + "=" * 80)
    print("  Analysis Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
