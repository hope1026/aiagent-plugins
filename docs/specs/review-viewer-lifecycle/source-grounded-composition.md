# 근거 기반 설명 구성과 이해 검증

적용 범위: 이 문서의 구조화 source·renderer·composition·freshness 계약은 [관리형 제작 경로](presentation-routing.md)에 적용한다. 일회성 자유 작성에는 해당 빌드 절차나 표현 제약을 강제하지 않는다.

## Requirements

### Visual Docs의 composition은 선택한 source와 요청 목적을 읽고 독자가 이해하거나 결정할 핵심 질문과 그 답의 설명 순서를 정해야 한다. 문서 종류, heading 이름과 profile은 구성의 참고 정보로 사용해야 한다.

짧은 문서는 간결한 설명만으로 충분할 수 있다. 모든 문서에 같은 섹션, 순서, 도표나 표를 요구하지 않는다. 독자 또는 목적이 실제로 달라지는 경우 질문·설명·강조가 그 차이를 반영해야 하며, label만 바꾸는 것으로 충족하지 않는다.

### Composition은 원문에 근거한 쉬운 설명, 명시된 사실의 묶음과 계산 예시를 허용하되 의무 강도, 조건, 예외, 수치, 책임과 확정 상태를 보존해야 한다. 원문 인용과 규범적 문장은 별도 상세에서 exact source로 유지해야 한다.

설명은 원문의 권위를 대신하지 않는다. Current·comparison·context의 역할과 Brief·Plan·Spec·Project의 source ownership을 그대로 유지한다. 이해를 돕기 위해 원본 Spec에 장식용 heading이나 diagram을 추가하도록 강제하지 않는다.

### 각 설명과 시각 관계에는 source reference와 확인 가능한 원문 근거가 연결되어야 하며, 예시의 가정은 source 값과 구분해야 한다. Source가 답을 제공하지 않으면 그 부족을 표시하고 새로운 정책, 인과 관계나 결정을 만들지 않아야 한다.

자동 관계 추출은 보조 경로다. 일반 문장에 명시된 정상 동작, 조건과 예외도 composition으로 설명할 수 있다. 유효한 source reference가 있다는 사실은 해당 설명의 의미를 보증하지 않는다.

### 공개 builder는 source와 View Context를 읽기 전용 준비 데이터로 제공하고 저장된 composition을 입력받아야 한다. Composition은 source hash와 View Context에 묶여야 하며 불일치하면 출력을 쓰기 전에 거부해야 한다.

현재 작업을 수행하는 agent가 composition을 작성한다. 외부 API나 별도 서비스, 특정 모델 설정을 필수 조건으로 추가하지 않는다. 제한된 데이터는 공통 renderer가 표현하며 문서별 HTML·CSS·script 작성과 생성 HTML 직접 편집은 허용하지 않는다.

### 생성 manifest는 사용한 generator와 고정 composition을 식별하고 source-browser와 읽기 검증이 필요한 설명 문서를 구분해야 한다. Source 또는 composition이 바뀌면 관련 의미·읽기 증거를 다시 확인하고 명시적 요청 없이 문서를 갱신하지 않아야 한다.

기본 source-browser는 원문 접근을 위한 fallback이다. 설명 composition이 검증을 통과해 렌더링되어도 읽기 검증 전에는 완성된 이해 문서로 표시하지 않는다. 재현성은 source, 저장된 composition, generator와 고정 build options의 조합에 적용한다.

### Visual Docs 완료 판단은 기계적 검증, 의미 충실도 검토와 실제 출력의 읽기·표시 검증을 분리해야 한다. Schema 통과, 원문 coverage와 유효한 근거 참조만으로 설명 정확성이나 인간 이해 성과를 주장하지 않아야 한다.

기계적 검증은 형식·출처·원문 접근·참조·재현성을 다룬다. 의미 검토는 조건·예외·의무 강도·수치·상태와 source 역할을 다룬다. 읽기 검증은 첫 읽기 경로에서 질문에 답할 수 있는지와 근거 이동·실제 표시를 다룬다. 하나의 통과를 다른 증거로 대체하지 않는다.

### Forge Visual Docs tooling의 이해 품질 검증은 생성 전에 정한 핵심 질문과 기대 답을 사용하고 작성에 쓰지 않은 자료를 포함해야 한다. 출력만 읽은 검토자의 답을 비교해 중대한 의미 왜곡과 주요 질문 누락을 수정하고 인간 관찰과 agent 평가를 구분해야 한다.

한국어와 영어, 짧은 Brief, 실행 Plan, prose workflow·정책·장문 system Spec, Project Handbook과 불충분 source를 평가 범위에 포함한다. Diagram 개수, test 개수와 component 존재는 이해 성과 지표가 아니다.

## Acceptance Criteria

### 서로 다른 독자 목적을 가진 동일 자료와 짧은 Brief를 composition으로 생성하면 필요한 질문과 답이 첫 읽기 경로에 반영되고 짧은 자료에는 불필요한 diagram과 고정 섹션이 강제되지 않는다.

검증하는 요구사항:

- [Visual Docs의 composition은 선택한 source와 요청 목적을 읽고 독자가 이해하거나 결정할 핵심 질문과 그 답의 설명 순서를 정해야 한다. 문서 종류, heading 이름과 profile은 구성의 참고 정보로 사용해야 한다.](source-grounded-composition.md#visual-docs의-composition은-선택한-source와-요청-목적을-읽고-독자가-이해하거나-결정할-핵심-질문과-그-답의-설명-순서를-정해야-한다-문서-종류-heading-이름과-profile은-구성의-참고-정보로-사용해야-한다)

### 조건과 예외를 가진 prose workflow와 정책 fixture를 설명 문서로 생성하면 쉬운 설명과 비교에서 원문의 의미와 역할이 유지되고 각 근거와 exact 원문으로 이동할 수 있다. 가정이 있는 계산 예시는 source 값과 가정을 구분한다.

검증하는 요구사항:

- [Composition은 원문에 근거한 쉬운 설명, 명시된 사실의 묶음과 계산 예시를 허용하되 의무 강도, 조건, 예외, 수치, 책임과 확정 상태를 보존해야 한다. 원문 인용과 규범적 문장은 별도 상세에서 exact source로 유지해야 한다.](source-grounded-composition.md#composition은-원문에-근거한-쉬운-설명-명시된-사실의-묶음과-계산-예시를-허용하되-의무-강도-조건-예외-수치-책임과-확정-상태를-보존해야-한다-원문-인용과-규범적-문장은-별도-상세에서-exact-source로-유지해야-한다)
- [각 설명과 시각 관계에는 source reference와 확인 가능한 원문 근거가 연결되어야 하며, 예시의 가정은 source 값과 구분해야 한다. Source가 답을 제공하지 않으면 그 부족을 표시하고 새로운 정책, 인과 관계나 결정을 만들지 않아야 한다.](source-grounded-composition.md#각-설명과-시각-관계에는-source-reference와-확인-가능한-원문-근거가-연결되어야-하며-예시의-가정은-source-값과-구분해야-한다-source가-답을-제공하지-않으면-그-부족을-표시하고-새로운-정책-인과-관계나-결정을-만들지-않아야-한다)

### 공개 CLI로 준비한 source·context에 맞는 composition을 입력하면 공통 renderer 출력이 생성되고, source 또는 context를 변경한 입력과 executable markup은 output 쓰기 전에 거부된다.

검증하는 요구사항:

- [공개 builder는 source와 View Context를 읽기 전용 준비 데이터로 제공하고 저장된 composition을 입력받아야 한다. Composition은 source hash와 View Context에 묶여야 하며 불일치하면 출력을 쓰기 전에 거부해야 한다.](source-grounded-composition.md#공개-builder는-source와-view-context를-읽기-전용-준비-데이터로-제공하고-저장된-composition을-입력받아야-한다-composition은-source-hash와-view-context에-묶여야-하며-불일치하면-출력을-쓰기-전에-거부해야-한다)

### 같은 source와 고정 composition·generator·build options를 재사용하면 동일 출력이 생성되고, composition 없는 source-browser와 읽기 검증이 남은 설명 문서의 상태가 구분된다. Source나 composition 변경만으로 자동 갱신되지 않는다.

검증하는 요구사항:

- [생성 manifest는 사용한 generator와 고정 composition을 식별하고 source-browser와 읽기 검증이 필요한 설명 문서를 구분해야 한다. Source 또는 composition이 바뀌면 관련 의미·읽기 증거를 다시 확인하고 명시적 요청 없이 문서를 갱신하지 않아야 한다.](source-grounded-composition.md#생성-manifest는-사용한-generator와-고정-composition을-식별하고-source-browser와-읽기-검증이-필요한-설명-문서를-구분해야-한다-source-또는-composition이-바뀌면-관련-의미읽기-증거를-다시-확인하고-명시적-요청-없이-문서를-갱신하지-않아야-한다)

### 원문 coverage만 충족한 접힌 원문 화면과 유효한 근거가 붙었지만 의미가 틀린 설명을 평가하면 각각 질문 누락과 의미 왜곡으로 실패하고 schema 통과가 완료 증거로 사용되지 않는다.

검증하는 요구사항:

- [Visual Docs 완료 판단은 기계적 검증, 의미 충실도 검토와 실제 출력의 읽기·표시 검증을 분리해야 한다. Schema 통과, 원문 coverage와 유효한 근거 참조만으로 설명 정확성이나 인간 이해 성과를 주장하지 않아야 한다.](source-grounded-composition.md#visual-docs-완료-판단은-기계적-검증-의미-충실도-검토와-실제-출력의-읽기표시-검증을-분리해야-한다-schema-통과-원문-coverage와-유효한-근거-참조만으로-설명-정확성이나-인간-이해-성과를-주장하지-않아야-한다)

### 생성 전 고정한 질문과 기대 답으로 Brief·Plan·Spec·Project 및 작성에 쓰지 않은 자료의 출력을 평가하면 질문별 정답·오답·누락과 원문 탐색 의존이 기록되고 agent 평가와 실제 인간 관찰이 별도로 보고된다.

검증하는 요구사항:

- [Forge Visual Docs tooling의 이해 품질 검증은 생성 전에 정한 핵심 질문과 기대 답을 사용하고 작성에 쓰지 않은 자료를 포함해야 한다. 출력만 읽은 검토자의 답을 비교해 중대한 의미 왜곡과 주요 질문 누락을 수정하고 인간 관찰과 agent 평가를 구분해야 한다.](source-grounded-composition.md#forge-visual-docs-tooling의-이해-품질-검증은-생성-전에-정한-핵심-질문과-기대-답을-사용하고-작성에-쓰지-않은-자료를-포함해야-한다-출력만-읽은-검토자의-답을-비교해-중대한-의미-왜곡과-주요-질문-누락을-수정하고-인간-관찰과-agent-평가를-구분해야-한다)
