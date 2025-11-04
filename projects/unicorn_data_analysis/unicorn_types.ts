/**
 * UMIS Unicorn Companies Database
 * TypeScript Type Definitions
 * 
 * Generated: 2025-11-04
 * Total Companies: 800
 */

export interface FundingRound {
  /** 펀딩 날짜 (예: "2019", "2019.Apr") */
  date: string;
  
  /** 펀딩 금액 (예: "100M", "1.5B") */
  amount: string;
  
  /** 통화 코드 (USD, EUR, GBP, BRL 등) */
  currency: "USD" | "EUR" | "GBP" | "BRL" | string;
  
  /** 투자자 목록 */
  investors: string[];
}

export interface BusinessInfo {
  /** 비즈니스 요약 (주요 설명) */
  summary: string;
  
  /** 상세 정보 목록 */
  details: string[];
}

export interface Valuation {
  /** 밸류에이션 (예: "$140.00") */
  amount_billion: string;
  
  /** 유니콘 등재일 (예: "2017.4.7") */
  date_added: string;
}

export interface Location {
  /** 국가명 */
  country: string;
}

export interface UnicornCompany {
  /** 회사명 */
  company: string;
  
  /** 밸류에이션 정보 */
  valuation: Valuation;
  
  /** 위치 정보 */
  location: Location;
  
  /** 산업 카테고리 */
  category: string;
  
  /** 주요 투자자 목록 */
  select_investors: string[];
  
  /** 펀딩 히스토리 */
  funding_history: FundingRound[];
  
  /** 비즈니스 정보 */
  business: BusinessInfo;
}

export interface DataMetadata {
  /** 총 기업 수 */
  total_companies: number;
  
  /** 데이터 버전 */
  data_version: string;
  
  /** 최종 업데이트 날짜 */
  last_updated: string;
  
  /** 데이터 구조 설명 */
  structure: {
    valuation: string;
    location: string;
    funding_history: string;
    business: string;
  };
}

export interface UnicornDatabase {
  /** 메타데이터 */
  metadata: DataMetadata;
  
  /** 유니콘 기업 목록 */
  companies: UnicornCompany[];
}

// ============================================
// 유틸리티 타입들
// ============================================

/** 국가별 기업 그룹 */
export type CompaniesByCountry = Record<string, UnicornCompany[]>;

/** 카테고리별 기업 그룹 */
export type CompaniesByCategory = Record<string, UnicornCompany[]>;

/** 투자자별 투자 기업 */
export type InvestorPortfolio = Record<string, {
  companies: string[];
  total_investments: number;
}>;

// ============================================
// 헬퍼 함수 예시
// ============================================

/**
 * 펀딩 금액을 백만 달러 단위로 변환
 */
export function parseFundingAmount(amount: string): number {
  const value = parseFloat(amount.replace(/[MB]/g, ''));
  if (amount.includes('B')) {
    return value * 1000;
  }
  return value;
}

/**
 * 총 펀딩 금액 계산 (백만 달러)
 */
export function calculateTotalFunding(company: UnicornCompany): number {
  return company.funding_history.reduce((total, round) => {
    return total + parseFundingAmount(round.amount);
  }, 0);
}

/**
 * 국가별 기업 그룹화
 */
export function groupByCountry(companies: UnicornCompany[]): CompaniesByCountry {
  return companies.reduce((acc, company) => {
    const country = company.location.country;
    if (!acc[country]) {
      acc[country] = [];
    }
    acc[country].push(company);
    return acc;
  }, {} as CompaniesByCountry);
}

/**
 * 카테고리별 기업 그룹화
 */
export function groupByCategory(companies: UnicornCompany[]): CompaniesByCategory {
  return companies.reduce((acc, company) => {
    const category = company.category;
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(company);
    return acc;
  }, {} as CompaniesByCategory);
}

/**
 * 투자자 포트폴리오 분석
 */
export function analyzeInvestorPortfolio(companies: UnicornCompany[]): InvestorPortfolio {
  const portfolio: InvestorPortfolio = {};
  
  companies.forEach(company => {
    const allInvestors = new Set([
      ...company.select_investors,
      ...company.funding_history.flatMap(round => round.investors)
    ]);
    
    allInvestors.forEach(investor => {
      if (!portfolio[investor]) {
        portfolio[investor] = {
          companies: [],
          total_investments: 0
        };
      }
      portfolio[investor].companies.push(company.company);
      portfolio[investor].total_investments += 1;
    });
  });
  
  return portfolio;
}

// ============================================
// 사용 예시
// ============================================

/*
import data from './unicorn_companies_structured.json';
import type { UnicornDatabase, UnicornCompany } from './unicorn_types';

// 타입이 자동으로 추론됨
const database: UnicornDatabase = data;

// 1. Top 10 밸류에이션 기업
const topCompanies = database.companies
  .sort((a, b) => {
    const aVal = parseFloat(a.valuation.amount_billion.replace(/[$,]/g, ''));
    const bVal = parseFloat(b.valuation.amount_billion.replace(/[$,]/g, ''));
    return bVal - aVal;
  })
  .slice(0, 10);

// 2. Sequoia Capital이 투자한 기업
const sequoiaCompanies = database.companies.filter(company =>
  company.select_investors.some(investor => 
    investor.toLowerCase().includes('sequoia')
  )
);

// 3. 2021년 펀딩받은 기업
const funded2021 = database.companies.filter(company =>
  company.funding_history.some(round => 
    round.date.startsWith('2021')
  )
);

// 4. 평균 펀딩 라운드 수
const avgRounds = database.companies.reduce((sum, c) => 
  sum + c.funding_history.length, 0
) / database.companies.length;

// 5. Fintech 카테고리 기업들의 총 펀딩
const fintechFunding = database.companies
  .filter(c => c.category === 'Fintech')
  .reduce((total, c) => total + calculateTotalFunding(c), 0);
*/
