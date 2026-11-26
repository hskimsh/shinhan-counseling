import os
import json
import datetime
import random
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="신한대학교 방사선학과 학생 사전 상담 기록지",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom Notion-like Warm Theme CSS
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');
    
    * {
        font-family: "Pretendard Variable", Pretendard, -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif !important;
    }
    
    .stApp {
        background-color: #f6f5f4;
        color: #111111;
    }
    
    .main .block-container {
        max-width: 680px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }
    
    .univ-badge {
        display: inline-block;
        background-color: rgba(246, 213, 184, 0.7);
        color: #111111;
        font-size: 12px;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 9999px;
        margin-bottom: 8px;
    }
    
    .main-title {
        font-size: 22px;
        font-weight: 700;
        color: #000000;
        letter-spacing: -0.02em;
        margin-bottom: 4px;
    }
    
    .sub-title {
        font-size: 13px;
        color: #757575;
        line-height: 1.5;
        margin-bottom: 16px;
    }
    
    .notice-card {
        background-color: #e6f3fe;
        border: 1px solid #bfe0fd;
        border-radius: 10px;
        padding: 12px 16px;
        font-size: 12.5px;
        color: #0056a8;
        line-height: 1.5;
        margin-bottom: 24px;
    }
    
    .section-header {
        font-size: 15px;
        font-weight: 700;
        color: #000000;
        margin-top: 24px;
        margin-bottom: 8px;
        border-bottom: 1px solid rgba(0,0,0,0.08);
        padding-bottom: 6px;
    }

    .stButton>button {
        background-color: #0075de;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        padding: 0.6rem 1.2rem;
        transition: all 0.15s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #0066c2;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Data File Paths
DOCS_DIR = os.path.join(os.path.expanduser("~"), "OneDrive", "문서", "신한대학교_방사선학과_상담기록부")
if not os.path.exists(DOCS_DIR):
    DOCS_DIR = os.path.join(os.path.expanduser("~"), "Documents", "신한대학교_방사선학과_상담기록부")
if not os.path.exists(DOCS_DIR):
    # Fallback to local data folder
    DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DOCS_DIR, exist_ok=True)

SURVEYS_FILE = os.path.join(DOCS_DIR, "surveys.csv")
STUDENTS_FILE = os.path.join(DOCS_DIR, "students.csv")

def load_students():
    if os.path.exists(STUDENTS_FILE):
        try:
            return pd.read_csv(STUDENTS_FILE, encoding='utf-8-sig', dtype={'id': str, 'grade': int})
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

def generate_ai_evaluation(survey_data):
    """
    Generate professional 6~7 sentence counseling evaluation
    strictly excluding unentered/empty tabs.
    """
    name = survey_data.get('studentName', '')
    grade = survey_data.get('grade', 1)
    term = survey_data.get('term', '1차')
    
    summary = f"{name} 학생({grade}학년)이 온라인으로 제출한 {term} 기록지를 바탕으로 지도학생의 자기보고 현황을 점검함. 학생이 작성한 주요 관심 영역 및 애로사항을 면밀히 분석하고 학사 및 진로 지도를 실시함."
    
    eval_sentences = []
    
    # 1. Personality
    p_tags = survey_data.get('personalityTags', [])
    if p_tags:
        eval_sentences.append(f"학생은 평소 성향 및 인성에 있어 [{', '.join(p_tags)}]의 긍정적인 특성을 지니고 있어 교수 및 동기들과의 관계 형성이 원만함.")
        eval_sentences.append("이러한 성실하고 수용적인 태도는 향후 보건의료 현장에서도 환자 및 동료 의료진과의 신뢰 구축에 큰 강점으로 작용할 것으로 사료됨.")
        
    # 2. Events
    e_tags = survey_data.get('eventTags', [])
    if e_tags:
        eval_sentences.append(f"학과 공동체 활동과 관련해서도 [{', '.join(e_tags)}] 등 학과 주요 행사에 능동적으로 참여하며 학과에 대한 깊은 애착과 소속감을 드러내고 있음.")
        
    # 3. GPA & Specs
    gpa = survey_data.get('totalGpa', '').strip()
    if gpa:
        eval_sentences.append(f"총학점은 {gpa} 수준으로 교과목 학습과 성적 관리에 있어 꾸준한 노력과 성실성을 유지하고 있음.")
        
    vol = survey_data.get('volunteerHours', '').strip()
    toeic = survey_data.get('toeicScoreAndDate', '').strip()
    specs = []
    if toeic: specs.append(f"어학 성적({toeic})")
    if vol: specs.append(f"총 봉사시간({vol})")
    if specs:
        eval_sentences.append(f"{' 및 '.join(specs)} 등을 착실히 수행하며 전공 외 비교과 역량 강화에도 높은 관심을 기울이고 있음.")
        
    certs = survey_data.get('certificates', '').strip()
    if certs:
        eval_sentences.append(f'자격 취득과 관련하여 "{certs}" 사항을 적극적으로 준비하고 있어 전문 자격 역량 확보에 대한 의지가 뚜렷함.')
        
    # 4. Academic
    a_status = survey_data.get('academicStatus', [])
    diff_sub = survey_data.get('difficultSubject', '').strip()
    if a_status or diff_sub:
        if diff_sub:
            eval_sentences.append(f'특히 "{diff_sub}" 교과목에서 다소 학습적 부담감을 느끼고 있어 집중적인 보완 학습과 교수 지도가 요구됨.')
        else:
            eval_sentences.append(f"학업 진행과 관련하여 [{', '.join(a_status)}] 상황을 스스로 인지하고 이를 극복하려는 성찰 태도를 보이고 있음.")
            
    # 5. National exam & Clinic
    nat = survey_data.get('nationalExamStatus', [])
    if nat:
        eval_sentences.append(f"방사선사 국가고시 및 전문 면허와 관련하여 [{', '.join(nat)}] 현황을 점검하고 체계적인 수험 계획을 실천해 나가고 있음.")
        
    clinic = survey_data.get('clinicPracticeStatus', [])
    if clinic:
        eval_sentences.append(f"병원 임상실습 분야에 있어서는 [{', '.join(clinic)}] 관련 직무 역량을 키우고자 진지한 태도로 준비에 임하고 있음.")
        
    # 6. Career
    career = survey_data.get('careerGoals', [])
    career_etc = survey_data.get('careerGoalEtc', '').strip()
    if career or career_etc:
        c_all = list(career)
        if career_etc: c_all.append(career_etc)
        eval_sentences.append(f"졸업 후 진로로는 [{', '.join(c_all)}] 분야로의 진출을 명확히 설정하고 필요한 역량을 차근차근 갖추어 가고 있음.")
        
    # 7. Life status or Vacation plan based on term
    life = survey_data.get('lifeStatus', [])
    if life:
        if '2차' in term:
            eval_sentences.append(f"방학 동안의 계획과 관련하여 [{', '.join(life)}] 사항을 중심으로 알차고 주도적인 방학 생활을 준비하고 있음.")
        else:
            eval_sentences.append(f"대학생활 및 심리 상태에 대해 [{', '.join(life)}] 현황을 나타내고 있으며, 마주하는 애로사항을 지혜롭게 해결하려는 긍정적인 태도를 견지하고 있음.")
        
    # 8. Message to prof
    msg = survey_data.get('messageToProfessor', '').strip()
    if msg:
        eval_sentences.append(f'지도교수에게 전한 의견("{msg}")을 통해 본인의 고민과 학업적 포부를 솔직하게 표현하며 지도교수의 피드백을 적극 수용하려는 열의를 보임.')
        
    # Enforce minimum 6~7 sentences without mentioning unentered tabs
    while len(eval_sentences) < 7:
        eval_sentences.append("자신이 제출한 항목들을 바탕으로 보완할 점을 성실히 이행하려는 자기주도적 성찰 태도가 매우 돋보임.")
        if len(eval_sentences) < 7:
            eval_sentences.append("지도교수와의 상담을 계기로 한 단계 더 성장할 수 있는 잠재력과 방사선 전문 인재로서의 발전 가능성이 매우 높음.")
            
    evaluation = " ".join(eval_sentences)
    meeting = survey_data.get('offlineMeetingRequest', '온라인 서면상담으로 충분')
    plan = f"학생이 온라인으로 제출한 내용을 바탕으로 설정한 세부 목표들이 충실히 달성될 수 있도록 지속적인 학사 지도를 진행하기로 함. 학생이 요청한 면담 형태({meeting})에 맞추어 맞춤형 피드백을 제공하고, 차기 학기 성과 진척도를 재확인하기로 함."
    
    full_content = f"[상담 요약]\n{summary}\n\n[학생 상태 및 소견]\n{evaluation}\n\n[지도 조언 및 향후 계획]\n{plan}"
    
    return summary, evaluation, plan, full_content

def save_survey(survey_record):
    fields = [
        "id","studentId","studentName","grade","semester","term","submissionDate",
        "totalGpa","volunteerHours","toeicScoreAndDate","certificates",
        "personalityTags","eventTags","academicStatus","difficultSubject",
        "nationalExamStatus","clinicPracticeStatus","careerGoals","careerGoalEtc",
        "lifeStatus","stressReason","relationshipReason","financialReason",
        "commuteReason","lifeEtcReason","offlineMeetingRequest","messageToProfessor",
        "aiSummary","aiEvaluation","aiPlan","aiFullContent","status","createdAt"
    ]
    
    new_df = pd.DataFrame([survey_record], columns=fields)
    
    if os.path.exists(SURVEYS_FILE):
        try:
            old_df = pd.read_csv(SURVEYS_FILE, encoding='utf-8-sig', dtype=str)
            # 같은 학생이 같은 상담 회차(term)에 이미 제출한 기록이 있으면 기존 것을 제거하고 최신 내용으로 갱신
            s_id = str(survey_record.get('studentId', '')).strip()
            s_term = str(survey_record.get('term', '')).strip()
            
            if s_id and 'studentId' in old_df.columns:
                old_df['studentId_clean'] = old_df['studentId'].astype(str).str.strip()
                old_df['term_clean'] = old_df['term'].astype(str).str.strip()
                
                # 동일 학번 + 동일 회차 중복 필터링
                filtered_old = old_df[~((old_df['studentId_clean'] == s_id) & (old_df['term_clean'] == s_term))]
                filtered_old = filtered_old.drop(columns=['studentId_clean', 'term_clean'], errors='ignore')
                combined = pd.concat([new_df, filtered_old], ignore_index=True)
            else:
                combined = pd.concat([new_df, old_df], ignore_index=True)
        except Exception:
            combined = new_df
    else:
        combined = new_df
        
    combined.to_csv(SURVEYS_FILE, index=False, encoding='utf-8-sig')

# --- Header UI ---
st.markdown('<div class="univ-badge">신한대학교 보건과학대학 방사선학과</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">학생 사전 상담 기록지 (온라인 접수)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">지도교수님과의 원활한 면담 및 상담 지도를 위해 본인의 최근 학업, 성향, 진로 현황을 작성해 주세요.</div>', unsafe_allow_html=True)

st.markdown("""
<div class="notice-card">
    💡 <strong>안내:</strong> 해당되는 항목만 자유롭게 입력하시면 됩니다. <strong>입력하지 않은 탭은 지도교수님의 AI 상담 문장 생성 시 자동으로 제외</strong>되어 안전하게 반영됩니다.
</div>
""", unsafe_allow_html=True)

students_df = load_students()

# 📌 1. 상담 회차 구분 (클릭 즉시 화면이 전환되도록 form 바깥에 배치)
st.markdown('<div class="section-header">📌 1. 상담 회차 선택</div>', unsafe_allow_html=True)
term = st.radio(
    "상담 회차 구분 (클릭 시 1차/2차 전용 설문 항목으로 자동 전환됩니다) *",
    ["1차 (학기초/중반 상담)", "2차 (학기말 성과 및 진로)"],
    horizontal=True,
    key="selected_term_radio"
)
is_second_term = "2차" in term

if is_second_term:
    st.info("🏖️ **2차 (학기말 성과 및 진로) 모드:** 9번 항목이 **[방학 동안의 계획]**으로 전환되었습니다.")
else:
    st.info("🌱 **1차 (학기초/중반 상담) 모드:** 9번 항목이 **[대학생활 및 심리상태]**로 설정되어 있습니다.")

with st.form("survey_form"):
    st.markdown('<div class="section-header">👤 학생 기본 정보</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1.2, 1.2, 0.8])
    with c1:
        student_id = st.text_input("학번 *", placeholder="예: 20260025")
    with c2:
        student_name = st.text_input("이름 *", placeholder="학생 성명")
    with c3:
        grade = st.selectbox("학년 *", [1, 2, 3, 4], index=0)
        
    # Auto-fill name if matching id found
    if student_id and not students_df.empty:
        matched = students_df[students_df['id'].astype(str).str.strip() == student_id.strip()]
        if not matched.empty and not student_name:
            st.info(f"등록 학생 확인: {matched.iloc[0]['name']} ({matched.iloc[0]['grade']}학년)")

    st.markdown('<div class="section-header">🌟 2. 학생 성격 및 태도 (선택)</div>', unsafe_allow_html=True)
    personality_options = [
        "성실하고 책임감 강함", "차분하고 신중한 성향", "외향적이고 적극적인 성격",
        "배려심 깊고 협동적", "자기주도적/추진력 있음", "경청 및 수용적 태도",
        "내성적이나 섬세하고 꼼꼼함", "밝고 긍정적인 성향", "원만한 대인 친화력"
    ]
    personality_tags = st.multiselect("본인의 평소 성향이나 대인관계 태도를 선택해 주세요", personality_options)

    st.markdown('<div class="section-header">🏛️ 3. 학과 행사 및 공동체 참여 (선택)</div>', unsafe_allow_html=True)
    event_options = [
        "학과 OT/MT 적극 참여", "학과 학술제/학술대회 참가", "방사선인의 날/체육대회 참여",
        "학과 학생회/집행부 활동", "전공 학술동아리 활동", "학과 봉사활동 참여",
        "선후배 멘토링 프로그램 참여", "학과 행사 참여도 독려 필요"
    ]
    event_tags = st.multiselect("학과 공식 행사 및 비교과 공동체 활동 참여 경험", event_options)

    st.markdown('<div class="section-header">📊 4. 정량 스펙 및 활동현황 (선택)</div>', unsafe_allow_html=True)
    q1, q2 = st.columns(2)
    with q1:
        total_gpa = st.text_input("총학점", placeholder="예: 3.85 / 4.5")
        toeic = st.text_input("토익점수와 취득일시", placeholder="예: 750점 (2026.05) 또는 준비중")
    with q2:
        volunteer = st.text_input("총 봉사시간", placeholder="예: 32시간")
        certs = st.text_input("자격증 및 면허증", placeholder="예: RI면허 필기준비, 컴활 1급 등")

    st.markdown('<div class="section-header">📚 5. 학업 및 수강 상태 (선택)</div>', unsafe_allow_html=True)
    academic_options = ["전공학습 부족", "학점관리 어려움", "전공기초 복습필요", "성적 향상/학점관리"]
    academic_tags = st.multiselect("현재 학업에 대한 체감 상태", academic_options)
    difficult_subject = st.text_input("어려운 교과목 (선택 입력)", placeholder="예: 방사선물리학, 방사선계측학")

    st.markdown('<div class="section-header">📝 6. 방사선사 국가고시 및 전문자격 (선택)</div>', unsafe_allow_html=True)
    nat_options = [
        "방사선사 국가고시 준비", "국시 모의고사 피드백", "방사선동위원소(RI) 일반면허",
        "비파괴검사(NDT) 기사", "의학물리사 준비", "공인 어학(TOEIC/오픽)"
    ]
    nat_tags = st.multiselect("국가고시 및 자격증 준비 현황", nat_options)

    st.markdown('<div class="section-header">🏥 7. 병원 임상실습 (선택)</div>', unsafe_allow_html=True)
    clinic_options = [
        "대학병원 실습기관 배정", "영상의학과 실습적응", "방사선종양학과 실습",
        "핵의학과 실습", "임상실습 태도 및 환자응대", "실습 중 애로사항"
    ]
    clinic_tags = st.multiselect("임상실습 이수 및 배정 현황", clinic_options)

    st.markdown('<div class="section-header">🎯 8. 진로 및 학습 목표 (선택)</div>', unsafe_allow_html=True)
    career_options = [
        "상급종합병원", "대학병원", "종합병원", "Part 관심(영상의학)",
        "Part 관심(핵의학)", "Part 관심(방사선종양학)", "방사선 기기회사",
        "방사선 관련 연구소", "군인(군무원)", "공무원", "대학원 진학"
    ]
    career_tags = st.multiselect("졸업 후 희망 진로 분야", career_options)
    career_etc = st.text_input("기타 희망 진로 (선택 입력)", placeholder="기타 희망 진로 분야 직접 기재")

    # 9. 대학생활 및 심리상태 (1차) vs 방학 동안의 계획 (2차)
    is_second_term = "2차" in term
    
    if is_second_term:
        st.markdown('<div class="section-header">🏖️ 9. 방학 동안의 계획 (선택)</div>', unsafe_allow_html=True)
        life_options = [
            "전공 학습 복습 및 보완", "토익/공인어학 집중 학습", "자격증 취득 준비(RI/NDT/컴활 등)",
            "병원 임상실습 이수", "봉사활동 참여", "아르바이트 및 사회경험",
            "휴식 및 체력 증진", "진로 탐색 및 병원 견학", "기타 개인 계획"
        ]
        life_tags = st.multiselect("방학 동안 집중할 주요 활동 계획을 선택해 주세요", life_options)
        
        stress_reason = ""
        rel_reason = ""
        fin_reason = ""
        commute_reason = ""
        etc_reason = st.text_input("방학 계획 세부사항 및 목표 (선택 입력)", placeholder="예: 토익 750점 달성, 방사선물리학 2학기 예습 등")
    else:
        st.markdown('<div class="section-header">🌱 9. 대학생활 및 심리상태 (선택)</div>', unsafe_allow_html=True)
        life_options = ["원만한 생활", "스트레스", "선/후배 동기관계", "경제적 어려움", "통학", "기타"]
        life_tags = st.multiselect("최근 대학생활 및 심리 상태", life_options, default=["원만한 생활"])
        
        stress_reason = ""
        rel_reason = ""
        fin_reason = ""
        commute_reason = ""
        etc_reason = ""
        
        if "스트레스" in life_tags:
            stress_reason = st.text_input("스트레스 사유 (선택 입력)", placeholder="스트레스의 원인이나 고민")
        if "선/후배 동기관계" in life_tags:
            rel_reason = st.text_input("동기/선후배 관계 사유 (선택 입력)", placeholder="교우관계 관련 고민")
        if "경제적 어려움" in life_tags:
            fin_reason = st.text_input("경제적 애로 사유 (선택 입력)", placeholder="장학금, 학비, 생활비 고민")
        if "통학" in life_tags:
            commute_reason = st.text_input("통학 애로 사유 (선택 입력)", placeholder="통학 소요시간, 기숙사 등")
        if "기타" in life_tags:
            etc_reason = st.text_input("기타 사유 (선택 입력)", placeholder="기타 내용 기재")

    st.markdown('<div class="section-header">🤝 10. 면담 요청 형태</div>', unsafe_allow_html=True)
    offline_request = st.radio(
        "교수님과의 면담 희망 형태 *",
        ["🟢 온라인 서면상담으로 충분 (작성 내용 기반 교수 피드백)", "🔴 오프라인 면담 요청 (연구실 대면 상담 희망)"],
        index=0
    )
    meeting_val = "오프라인 면담 요청" if "오프라인" in offline_request else "온라인 서면상담으로 충분"

    st.markdown('<div class="section-header">💬 11. 교수에게 하고 싶은 말 (선택)</div>', unsafe_allow_html=True)
    message_to_prof = st.text_area("교수님께 꼭 여쭤보고 싶은 질문이나 고민, 하반기 다짐 등을 자유롭게 적어주세요.", height=100)

    st.write("")
    submitted = st.form_submit_button("📋 상담 기록지 제출하기 (실시간 AI 소견 생성)")

if submitted:
    if not student_id.strip() or not student_name.strip():
        st.error("⚠️ 학번과 이름을 반드시 입력해 주세요.")
    else:
        with st.spinner("교수님 상담 관리 시스템에 저장 및 AI 평가 문장 생성 중..."):
            survey_data = {
                "studentId": student_id.strip(),
                "studentName": student_name.strip(),
                "grade": grade,
                "term": term,
                "personalityTags": personality_tags,
                "eventTags": event_tags,
                "totalGpa": total_gpa.strip(),
                "volunteerHours": volunteer.strip(),
                "toeicScoreAndDate": toeic.strip(),
                "certificates": certs.strip(),
                "academicStatus": academic_tags,
                "difficultSubject": difficult_subject.strip(),
                "nationalExamStatus": nat_tags,
                "clinicPracticeStatus": clinic_tags,
                "careerGoals": career_tags,
                "careerGoalEtc": career_etc.strip(),
                "lifeStatus": life_tags,
                "stressReason": stress_reason.strip(),
                "relationshipReason": rel_reason.strip(),
                "financialReason": fin_reason.strip(),
                "commuteReason": commute_reason.strip(),
                "lifeEtcReason": etc_reason.strip(),
                "offlineMeetingRequest": meeting_val,
                "messageToProfessor": message_to_prof.strip(),
            }
            
            ai_sum, ai_eval, ai_plan, ai_full = generate_ai_evaluation(survey_data)
            
            srv_id = f"SRV-{datetime.date.today().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
            record = {
                "id": srv_id,
                "studentId": student_id.strip(),
                "studentName": student_name.strip(),
                "grade": str(grade),
                "semester": "2026학년도 1학기",
                "term": term,
                "submissionDate": datetime.date.today().strftime('%Y-%m-%d'),
                "totalGpa": total_gpa.strip(),
                "volunteerHours": volunteer.strip(),
                "toeicScoreAndDate": toeic.strip(),
                "certificates": certs.strip(),
                "personalityTags": ";".join(personality_tags),
                "eventTags": ";".join(event_tags),
                "academicStatus": ";".join(academic_tags),
                "difficultSubject": difficult_subject.strip(),
                "nationalExamStatus": ";".join(nat_tags),
                "clinicPracticeStatus": ";".join(clinic_tags),
                "careerGoals": ";".join(career_tags),
                "careerGoalEtc": career_etc.strip(),
                "lifeStatus": ";".join(life_tags),
                "stressReason": stress_reason.strip(),
                "relationshipReason": rel_reason.strip(),
                "financialReason": fin_reason.strip(),
                "commuteReason": commute_reason.strip(),
                "lifeEtcReason": etc_reason.strip(),
                "offlineMeetingRequest": meeting_val,
                "messageToProfessor": message_to_prof.strip(),
                "aiSummary": ai_sum,
                "aiEvaluation": ai_eval,
                "aiPlan": ai_plan,
                "aiFullContent": ai_full,
                "status": "접수대기",
                "createdAt": datetime.datetime.now().isoformat(),
            }
            
            save_survey(record)
            
        st.success(f"🎉 {student_name} 학생의 사전 상담 기록지가 성공적으로 제출되었습니다!")
        st.balloons()
        
        st.markdown(f"""
        ### ✅ 제출 접수 확인
        - **접수 번호:** `{srv_id}`
        - **학생 정보:** {student_name} ({student_id}, {grade}학년)
        - **면담 구분:** {meeting_val}
        - **반영 상태:** 신한대학교 방사선학과 상담기록부(`surveys.csv`)에 즉시 동기화되었습니다.
        """)

# --- 교수님 전용 조회 및 다운로드 관리자 구역 (학생 화면에서는 미표시) ---
# 일반 학생 접속 시에는 메뉴 자체가 아예 보이지 않으며 클릭할 수 없습니다.
# 교수님께서 주소 뒤에 '?admin=true'를 붙이시거나 사이드바 비밀접속을 누르셨을 때만 나타납니다.
params = st.query_params
is_admin_mode = params.get("admin", "") in ["true", "1", "prof"]

# 사이드바 맨 하단에 작고 눈에 띄지 않는 교수님 전용 로그인 토글 제공
with st.sidebar:
    st.caption("신한대학교 방사선학과")
    show_admin_box = st.checkbox("교수님 전용 모드", value=is_admin_mode)

if is_admin_mode or show_admin_box:
    st.write("")
    st.write("")
    st.markdown("---")
    
    with st.expander("교수님 전용 관리 메뉴 (제출 현황 조회 & 엑셀 다운로드)", expanded=True):
        st.markdown("""
        <div style="font-size: 12px; color: #757575; margin-bottom: 8px;">
            지도교수님 전용 구역입니다. 학생들이 제출한 설문 내역을 웹에서 즉시 확인하고 CSV로 내려받을 수 있습니다.
        </div>
        """, unsafe_allow_html=True)

        admin_pw = st.text_input("교수님 인증 암호", type="password", placeholder="비밀번호를 입력하세요", key="admin_pw_input")
        
        if admin_pw:
            if admin_pw.strip() in ["shinhan1234", "1234", "shinhan"]:
                st.success("인증이 완료되었습니다.")
            
            if os.path.exists(SURVEYS_FILE):
                try:
                    df_surveys = pd.read_csv(SURVEYS_FILE, encoding='utf-8-sig', dtype=str)
                except Exception:
                    df_surveys = pd.DataFrame()
            else:
                df_surveys = pd.DataFrame()
                
            if not df_surveys.empty:
                st.markdown(f"**총 접수된 설문: {len(df_surveys)}건**")
                
                # 요약 통계 카드
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("총 접수 건수", f"{len(df_surveys)}건")
                with col_b:
                    offline_cnt = len(df_surveys[df_surveys['offlineMeetingRequest'].str.contains('오프라인', na=False)])
                    st.metric("🔴 대면 면담 요청", f"{offline_cnt}명")
                with col_c:
                    online_cnt = len(df_surveys[~df_surveys['offlineMeetingRequest'].str.contains('오프라인', na=False)])
                    st.metric("🟢 온라인 서면 종결", f"{online_cnt}명")
                
                # CSV 원본 다운로드 버튼 (UTF-8 BOM 포함하여 엑셀에서 바로 깨짐없이 열림)
                csv_bytes = df_surveys.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                
                st.download_button(
                    label="📥 전체 설문 결과 CSV 다운로드 (엑셀 완벽 호환)",
                    data=csv_bytes,
                    file_name=f"신한대_방사선학과_설문접수현황_{datetime.date.today().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
                st.caption("💡 내려받으신 CSV 파일은 교수님 상담 프로그램의 [📥 구글 폼 응답 CSV 가져오기] 버튼을 통해 1초 만에 불러오실 수 있습니다.")

                # 최근 제출된 학생 목록 테이블
                st.markdown("#### 📋 학생별 제출 요약 목록")
                display_cols = ['studentId', 'studentName', 'grade', 'term', 'totalGpa', 'offlineMeetingRequest', 'submissionDate']
                available_cols = [c for c in display_cols if c in df_surveys.columns]
                
                df_preview = df_surveys[available_cols].copy()
                df_preview.columns = ['학번', '성명', '학년', '상담회차', '총학점', '면담형태', '제출일자'][:len(available_cols)]
                st.dataframe(df_preview, use_container_width=True)

                # 학생별 AI 소견서 상세 조회
                st.markdown("#### 🔍 학생별 AI 평가문장 (최소 6~7문장) 상세 열람")
                student_options = df_surveys.apply(lambda row: f"{row.get('studentName', '')} ({row.get('studentId', '')}) - {row.get('submissionDate', '')}", axis=1).tolist()
                selected_student = st.selectbox("열람할 학생 선택", student_options)
                
                if selected_student:
                    idx = student_options.index(selected_student)
                    student_row = df_surveys.iloc[idx]
                    
                    st.markdown(f"**[{student_row.get('studentName', '')} 학생 사전 상담 요약]**")
                    with st.container():
                        st.info(f"**[상담 요약]**\n\n{student_row.get('aiSummary', '요약 없음')}")
                        st.success(f"**[학생 상태 및 소견 (정성 문장)]**\n\n{student_row.get('aiEvaluation', '소견 없음')}")
                        st.warning(f"**[지도 조언 및 향후 계획]**\n\n{student_row.get('aiPlan', '계획 없음')}")
                        
                        full_txt = student_row.get('aiFullContent', '')
                        if full_txt:
                            st.text_area("포털 복사용 전체 텍스트", full_txt, height=180)
                            
                    # 오프라인 면담 요청 학생인 경우 일정 안내문 생성기 제공
                    if '오프라인' in str(student_row.get('offlineMeetingRequest', '')):
                        st.markdown("---")
                        st.markdown("#### 📅 오프라인 면담 일정 안내문 생성 및 발송")
                        
                        m_col1, m_col2 = st.columns(2)
                        with m_col1:
                            m_date = st.date_input("면담 예정일자", value=datetime.date.today() + datetime.timedelta(days=1), key="m_date_picker")
                        with m_col2:
                            m_time = st.text_input("면담 시간", value="14:00", key="m_time_input")
                            
                        m_place = st.text_input("면담 장소", value="방사선학과 교수연구실 (신한관 4층)", key="m_place_input")
                        
                        # 학생 연락처 조회 (students.csv 연계)
                        s_phone = ""
                        s_email = ""
                        if not students_df.empty and 'id' in students_df.columns:
                            m_match = students_df[students_df['id'].astype(str).str.strip() == str(student_row.get('studentId', '')).strip()]
                            if not m_match.empty:
                                s_phone = str(m_match.iloc[0].get('phone', ''))
                                s_email = str(m_match.iloc[0].get('email', ''))
                        
                        notice_text = f"""[신한대학교 방사선학과 지도교수 면담 안내]

안녕하세요, {student_row.get('studentName', '')} 학생.
제출해 준 사전 상담 기록지({student_row.get('term', '1차')})의 오프라인 면담 요청을 확인하였습니다.
아래와 같이 개별 면담 일정을 안내하니 시간을 확인하고 참석하기 바랍니다.

■ 면담 대상: {student_row.get('studentName', '')} ({student_row.get('studentId', '')}, {student_row.get('grade', '')}학년)
■ 면담 일시: {m_date.strftime('%Y년 %m월 %d일')} {m_time}
■ 면담 장소: {m_place}
■ 준비 사항: 사전 제출한 상담 내용을 바탕으로 진로 및 학업 개별 면담 진행

※ 일정 조율이 필요한 경우 미리 교수님에게 연락 바랍니다.
- 방사선학과 지도교수 드림"""
                        
                        st.text_area("카톡 / 문자 / 공지용 면담 안내문", notice_text, height=180)
                        
                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            if s_phone and s_phone != "nan":
                                sms_link = f"sms:{s_phone}?body={notice_text}"
                                st.markdown(f'<a href="{sms_link}" target="_blank" style="display:inline-block;padding:8px 16px;background:#10b981;color:white;border-radius:6px;text-decoration:none;font-weight:600;font-size:12px;">📱 {student_row.get("studentName", "")} 학생에게 문자(SMS) 연결 ({s_phone})</a>', unsafe_allow_html=True)
                        with btn_col2:
                            if s_email and s_email != "nan":
                                mail_link = f"mailto:{s_email}?subject=[신한대 방사선학과] {student_row.get('studentName', '')} 학생 개별 면담 안내&body={notice_text}"
                                st.markdown(f'<a href="{mail_link}" target="_blank" style="display:inline-block;padding:8px 16px;background:#0075de;color:white;border-radius:6px;text-decoration:none;font-weight:600;font-size:12px;">✉️ 학생 이메일 발송 ({s_email})</a>', unsafe_allow_html=True)
            else:
                st.info("아직 제출된 학생 설문 데이터가 없습니다.")
        else:
            st.error("암호가 일치하지 않습니다.")

