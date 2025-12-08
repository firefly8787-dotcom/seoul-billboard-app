import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# ✅ 앱 시작 확인용 로그
st.write("✅ 앱이 시작되었습니다")

with st.expander("📘 설명서 보기"):
    st.markdown("""
### 🧾 서울 전광판 광고 필터 앱 사용 설명서

#### 🟦 앱 개요
- 이 앱은 **서울 주요 전광판 광고 현황을 조사월, 업종, 광고주 등으로 필터링하고 통계로 분석하는 도구**입니다.
- 팀원들이 **공통 포맷에 맞게 데이터를 입력하고 공유**할 수 있도록 제작되었습니다.

#### 🟩 사용 대상 구글시트
- 반드시 구글시트의 **`DATA` 시트**에만 입력해야 앱에서 인식됩니다.  
👉 [📄 원본 시트 바로가기](https://docs.google.com/spreadsheets/d/1AFotC96rl9nz1m2BDgn2mGSm3Jo69-mcGWAquYvWEwE/edit)

---

#### 🟨 필터 가능 항목 (앱 좌측)
- `조사월` (예: 202506 형식)
- `위치`, `빌딩&전광판`, `업종`: ✅ **드롭다운으로만 선택**
- `제품&브랜드`, `광고대행사`, `미디어렙사`, `광고주(연락처)`, `해외본사`: 자유입력

---

#### 🟥 입력 시 주의사항

✅ **광고주 이름의 정확한 통일성 유지가 핵심**입니다.  
필터가 작동하려면 **기존에 쓰인 광고주명과 정확히 일치**해야 하며,  
띄어쓰기·철자·괄호 차이로도 필터링이 되지 않을 수 있습니다.

| ❌ 잘못된 입력     | ✅ 올바른 입력   |
|------------------|----------------|
| 샤넬 코리아       | 샤넬코리아       |
| 구찌 KOREA       | 구찌코리아       |
| 디올(주)          | 디올코리아       |
| 쿠팡 주식회사     | 쿠팡            |

👉 **광고주명은 기존 입력값을 복사해서 붙여넣는 방식 권장**

---

#### 🧩 드롭다운(선택목록) 해제 방법

- `위치`, `빌딩&전광판`, `업종` 항목은 **기존 값만 선택할 수 있도록 드롭다운 제한**이 걸려 있습니다.
- 만약 **새로운 전광판 이름**이나 **신규 업종**을 추가하려면:

📌 **방법 1**:  
→ 구글시트 상단 메뉴에서  
`데이터 > 데이터 유효성 > 조건 해제` 또는 `리스트 직접 편집`

📌 **방법 2**:  
→ 새로운 값을 하단 빈 행에 자유롭게 입력한 후, 드롭다운 목록 범위를 확장  
예: `업종` 항목 → 드롭다운 범위를 C2:C1000 등으로 수정

💡 **입력 시 띄어쓰기·오타 주의** (필터링 결과에 직접 영향)

---

#### 📊 통계 기능

선택한 조사월/업종 기준으로 다음 통계가 자동 계산됩니다:

1. **📈 광고주별 광고 건수**
2. **🌍 해외본사별 광고 건수**

→ 필터에 맞게 **광고를 가장 많이 집행한 광고주/본사 순으로 정렬됨**

---

#### 📥 기타 안내

| 기능 | 설명 |
|------|------|
| CSV 다운로드 | 필터 결과는 다운로드 버튼으로 저장 가능 |
| 실시간 반영 | 구글시트에서 수정 즉시 앱에 반영됨 |
| 데이터 추가 | 새로운 전광판 열도 가능, 필요 시 변환 스크립트 제공 |

---

#### 📬 문의 및 운영
- 데이터 담당자: **dongsoo8787@naver.com**
- 앱 제작 및 유지관리: **동아미디어솔루션본부**
""")

# ✅ Streamlit secrets 인증 방식
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = st.secrets["google"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(creds_dict), scope)
client = gspread.authorize(creds)

# ✅ 구글시트에서 데이터 로드
spreadsheet = client.open_by_url(
    "https://docs.google.com/spreadsheets/d/1AFotC96rl9nz1m2BDgn2mGSm3Jo69-mcGWAquYvWEwE/edit"
)
worksheet = spreadsheet.worksheet("DATA")  # 시트명 정확히 'DATA'
data = pd.DataFrame(worksheet.get_all_records())

# 컬럼명 앞뒤 공백 제거 (안전용)
data.columns = data.columns.str.strip()

# ★★★ 이 세 줄을 추가해주세요 ★★★
for col in data.columns:
    if data[col].dtype == 'object':
        data[col] = data[col].astype(str).str.strip()
# ★★★ 여기까지 추가 ★★★

st.title("🎉서울 주요 전광판 광고주 조사🎉")

###############################################################################
# 🔹 권역 및 전광판 리스트 정의 (강남권 / 강북권)
###############################################################################
gangnam_buildings = [
    "K-POP Live",
    "현대백화점",
    "파르나스 미디어타워",
    "코엑스 미디어타워",
    "휴먼타워",
    "YK빌딩",
    "강남빌딩",
    "청담빌딩",
    "S&S타워",
    "로드블록12",
    "랜드마크타워",
    "마스터빌딩",
    "백송빌딩",
    "벤츠빌딩",
    "신웅타워",
    "썬타워",
    "엠포리아빌딩",
    "유경빌딩",
    "한섬빌딩",
    "BMW",
    "SB빌딩",
    "SGF청담타워",
    "SYH빌딩",
]

gangbuk_buildings = [
    "신세계스퀘어",
    "코리아나호텔(K-VISION)",
    "KT스퀘어",
    "교원내외빌딩",
    "룩스",
    "한국빌딩(ME)",
    "일민미술관",
    "을지한국빌딩",
    "명동N빌딩(MN)",
]


def classify_region(row: pd.Series) -> str:
    """빌딩&전광판 기준으로 강남권 / 강북권 분류"""
    b = str(row.get("빌딩&전광판", "")).strip()
    if b in gangnam_buildings:
        return "강남권"
    if b in gangbuk_buildings:
        return "강북권"
    return ""


# 🔎 권역별 전광판 기준을 페이지에 명시
st.markdown("### 📍 권역별 전광판 기준")
with st.expander("강남권 / 강북권 전광판 목록 보기", expanded=True):
    st.markdown("#### 🟦 강남권 전광판")
    st.markdown("- " + "\n- ".join(gangnam_buildings))

    st.markdown("#### 🟥 강북권 전광판")
    st.markdown("- " + "\n- ".join(gangbuk_buildings))

###############################################################################
# ✅ 필터 기능
###############################################################################
filter_columns = [
    "조사월",
    "위치",
    "빌딩&전광판",
    "업종",
    "제품&브랜드",
    "광고대행사(연락처) ",
    "미디어렙사(연락처)",
    "광고주(연락처)",
    "해외본사",
]

filters = {}
for col in filter_columns:
    if col in data.columns:
        options = sorted(data[col].astype(str).unique())
        filters[col] = st.multiselect(col, ["전체"] + options)

filtered_data = data.copy()
for col, selected in filters.items():
    if selected and "전체" not in selected:
        filtered_data = filtered_data[filtered_data[col].astype(str).isin(selected)]

st.markdown("### 🔍 필터 결과")
st.dataframe(filtered_data, use_container_width=True)

st.download_button(
    label="📥 필터 결과 CSV 다운로드",
    data=filtered_data.to_csv(index=False).encode("utf-8-sig"),
    file_name="filtered_billboard_data.csv",
    mime="text/csv",
)

###############################################################################
# ✅ 기본 통계 기능
###############################################################################
st.markdown("### 📈 월별 광고주별 광고 수")
month_options = sorted(data["조사월"].astype(str).unique())
selected_month = st.selectbox("조사월 선택", ["전체"] + month_options)

industry_options = sorted(data["업종"].astype(str).unique())
selected_industry = st.selectbox("업종 선택", ["전체"] + industry_options)

stat_data = data.copy()
if selected_month != "전체":
    stat_data = stat_data[stat_data["조사월"].astype(str) == selected_month]
if selected_industry != "전체":
    stat_data = stat_data[stat_data["업종"].astype(str) == selected_industry]

monthly_advertisers = (
    stat_data.groupby(["조사월", "광고주(연락처)"]).size().reset_index(name="건수")
)
st.dataframe(
    monthly_advertisers.sort_values(
        by=["조사월", "건수"], ascending=[True, False]
    ),
    use_container_width=True,
)

st.markdown("### 🌍 월별 해외본사 광고 수")
monthly_brands = (
    stat_data.groupby(["조사월", "해외본사"]).size().reset_index(name="건수")
)
st.dataframe(
    monthly_brands.sort_values(by=["조사월", "건수"], ascending=[True, False]),
    use_container_width=True,
)

###############################################################################
# 🟦 신규 기능 1: K-VISION & KT스퀘어 단독 광고 + 동일 기간 룩스 광고 분석
###############################################################################
st.markdown("## 🟦 K-VISION & KT스퀘어 단독 광고 분석 (룩스 제외 · 공익 제외)")
st.write(
    "선택한 조사월 범위에서 **공익 광고를 제외하고**, "
    "**코리아나호텔(K-VISION)**과 **KT스퀘어** 전광판에만 등장하며 "
    "**룩스에는 등장하지 않은 광고주**를 표로 나열합니다. "
    "추가로, 해당 광고주가 과거 **일민미술관·룩스**에 광고한 적이 있다면 그 조사월을 표시하고, "
    "동일 기간 기준으로 **룩스 광고주가 K-VISION / KT스퀘어와 어떤 조합으로 집행되었는지**도 별도 표로 보여줍니다."
)

multi_months = st.multiselect(
    "분석할 조사월 선택 (복수 선택 가능)",
    month_options,
    default=[],
)

if multi_months:
    base = data.copy()

    # 1) 선택 월 + 광화문만 + 공익 제외
    subset = base[
        (base["조사월"].astype(str).isin(multi_months))
        & (base["위치"] == "광화문")
        & (~base["업종"].astype(str).str.contains("공익", na=False))
    ]

    # 2) K-VISION / KT스퀘어 / 룩스 분리
    kvkt = subset[
        subset["빌딩&전광판"].isin(["코리아나호텔(K-VISION)", "KT스퀘어"])
    ]
    lux = subset[subset["빌딩&전광판"] == "룩스"]

    kvkt_adv = kvkt["광고주(연락처)"].astype(str)
    lux_adv = lux["광고주(연락처)"].astype(str).unique()

    # ① K-VISION & KT스퀘어 단독 광고주 (선택 기간 내 룩스 X)
    unique_kvkt = kvkt[~kvkt_adv.isin(lux_adv)].copy()

    grouped = (
        unique_kvkt.groupby("광고주(연락처)")
        .agg({"제품&브랜드": "first", "해외본사": "first"})
        .reset_index()
    )

    boards_per_adv = (
        unique_kvkt.groupby("광고주(연락처)")["빌딩&전광판"]
        .unique()
        .reset_index()
    )

    def label_board(arr):
        s = set(arr)
        has_kv = "코리아나호텔(K-VISION)" in s
        has_kt = "KT스퀘어" in s
        if has_kv and has_kt:
            return "K-VISION & KT스퀘어"
        elif has_kv:
            return "K-VISION"
        elif has_kt:
            return "KT스퀘어"
        return ""

    boards_per_adv["전광판 구분"] = boards_per_adv["빌딩&전광판"].apply(label_board)
    boards_per_adv = boards_per_adv[["광고주(연락처)", "전광판 구분"]]

    ilmin_rows = []
    for _, row in grouped.iterrows():
        adv = str(row["광고주(연락처)"])
        foreign_hq = str(row.get("해외본사", "") or "")
        nationality = "해외" if foreign_hq.strip() != "" else "국내"

        ilmin = base[
            (base["빌딩&전광판"] == "일민미술관")
            & (base["광고주(연락처)"].astype(str) == adv)
        ]
        months_ilmin = sorted(ilmin["조사월"].astype(str).unique())
        ilmin_months_str = ", ".join(months_ilmin) if months_ilmin else ""

        lux_hist = base[
            (base["빌딩&전광판"] == "룩스")
            & (base["광고주(연락처)"].astype(str) == adv)
        ]
        months_lux = sorted(lux_hist["조사월"].astype(str).unique())
        lux_months_str = ", ".join(months_lux) if months_lux else ""

        ilmin_rows.append((adv, nationality, ilmin_months_str, lux_months_str))

    ilmin_df = pd.DataFrame(
        ilmin_rows,
        columns=["광고주(연락처)", "국적", "일민미술관 광고월", "룩스 광고월"],
    )

    grouped = grouped.merge(boards_per_adv, on="광고주(연락처)", how="left")
    grouped = grouped.merge(ilmin_df, on="광고주(연락처)", how="left")

    grouped = grouped[
        [
            "광고주(연락처)",
            "제품&브랜드",
            "해외본사",
            "국적",
            "전광판 구분",
            "일민미술관 광고월",
            "룩스 광고월",
        ]
    ]

    st.markdown("### 1) K-VISION & KT스퀘어 단독 광고주 (선택 기간 내 룩스 없음)")
    st.dataframe(grouped, use_container_width=True)

    # ② 동일 기간 기준 룩스 광고주 (K-VISION / KT스퀘어 조합 포함)
    st.markdown("### 2) 동일 기간 룩스 광고주 (K-VISION / KT스퀘어 조합 포함)")

    lux_adv_unique = lux["광고주(연락처)"].astype(str).unique()

    lux_combo_base = subset[
        subset["광고주(연락처)"].astype(str).isin(lux_adv_unique)
        & subset["빌딩&전광판"].isin(
            ["룩스", "코리아나호텔(K-VISION)", "KT스퀘어"]
        )
    ].copy()

    if lux_combo_base.empty:
        st.info("선택한 기간 동안 룩스 광고주 데이터가 없습니다.")
    else:
        lux_grouped = (
            lux_combo_base.groupby("광고주(연락처)")
            .agg({"제품&브랜드": "first", "해외본사": "first"})
            .reset_index()
        )

        boards_per_adv2 = (
            lux_combo_base.groupby("광고주(연락처)")["빌딩&전광판"]
            .unique()
            .reset_index()
        )

        def label_lux_combo(arr):
            s = set(arr)
            has_lux = "룩스" in s
            has_kv = "코리아나호텔(K-VISION)" in s
            has_kt = "KT스퀘어" in s

            if has_lux and not has_kv and not has_kt:
                return "룩스 단독"
            if has_lux and has_kv and not has_kt:
                return "룩스 + K-VISION"
            if has_lux and not has_kv and has_kt:
                return "룩스 + KT스퀘어"
            if has_lux and has_kv and has_kt:
                return "룩스 + K-VISION + KT스퀘어"
            return "기타"

        boards_per_adv2["전광판 조합"] = boards_per_adv2["빌딩&전광판"].apply(
            label_lux_combo
        )
        boards_per_adv2 = boards_per_adv2[
            ["광고주(연락처)", "전광판 조합"]
        ]

        lux_rows = []
        for _, row in lux_grouped.iterrows():
            adv = str(row["광고주(연락처)"])
            foreign_hq = str(row.get("해외본사", "") or "")
            nationality = "해외" if foreign_hq.strip() != "" else "국내"

            lux_only = subset[
                (subset["빌딩&전광판"] == "룩스")
                & (subset["광고주(연락처)"].astype(str) == adv)
            ]
            months_lux = sorted(lux_only["조사월"].astype(str).unique())
            lux_months_str = ", ".join(months_lux) if months_lux else ""

            lux_rows.append((adv, nationality, lux_months_str))

        lux_info_df = pd.DataFrame(
            lux_rows, columns=["광고주(연락처)", "국적", "룩스 광고월"]
        )

        lux_grouped = lux_grouped.merge(
            boards_per_adv2, on="광고주(연락처)", how="left"
        )
        lux_grouped = lux_grouped.merge(
            lux_info_df, on="광고주(연락처)", how="left"
        )

        lux_grouped = lux_grouped[
            [
                "광고주(연락처)",
                "제품&브랜드",
                "해외본사",
                "국적",
                "전광판 조합",
                "룩스 광고월",
            ]
        ]

        st.dataframe(lux_grouped, use_container_width=True)
else:
    st.info(
        "분석할 조사월을 하나 이상 선택하면 K-VISION & KT스퀘어 / 룩스 조합 분석 결과가 표시됩니다."
    )

###############################################################################
# 🟥 신규 기능 2: 강남권 vs 강북권 업종/광고주 분포 비교 (공익 제외, 월 복수 선택)
###############################################################################
st.markdown("## 🟥 강남권 vs 강북권 비교 분석 (공익 제외)")

region_months = st.multiselect(
    "강남권 vs 강북권 비교에 사용할 조사월 선택 (선택 안 하면 전체 기간 기준)",
    month_options,
    default=[],
)

region_df = data.copy()
region_df["권역"] = region_df.apply(classify_region, axis=1)
region_df = region_df[region_df["권역"].isin(["강남권", "강북권"])]
region_df = region_df[region_df["업종"].astype(str).str.strip() != "공익"]

if region_months:
    region_df = region_df[region_df["조사월"].astype(str).isin(region_months)]

if not region_df.empty:
    if not region_months:
        title_suffix = " (전체 기간 기준)"
    else:
        title_suffix = " (" + ", ".join(region_months) + " 기준)"
else:
    title_suffix = ""
    st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    st.stop()

# -------------------------------------------------------------------------
# 🔹 업종별 강남/강북 건수 + 비중(%), 강남/강북 각각 비중 높은 순으로 정렬
# -------------------------------------------------------------------------
ind_counts = (
    region_df.groupby(["업종", "권역"]).size().reset_index(name="건수")
)

ind_pivot = (
    ind_counts.pivot(index="업종", columns="권역", values="건수").fillna(0)
)

for col in ["강남권", "강북권"]:
    if col not in ind_pivot.columns:
        ind_pivot[col] = 0

ind_pivot["총 건수"] = ind_pivot["강남권"] + ind_pivot["강북권"]
ind_pivot["강남권 비중(%)"] = (
    ind_pivot["강남권"] / ind_pivot["총 건수"].replace(0, 1) * 100
).round(1)
ind_pivot["강북권 비중(%)"] = (
    ind_pivot["강북권"] / ind_pivot["총 건수"].replace(0, 1) * 100
).round(1)

# 강남 기준 정렬
gn_sorted = (
    ind_pivot.sort_values("강남권 비중(%)", ascending=False)
    .reset_index()
)
gn_sorted.insert(0, "강남 순위", range(1, len(gn_sorted) + 1))

# 강북 기준 정렬
gb_sorted = (
    ind_pivot.sort_values("강북권 비중(%)", ascending=False)
    .reset_index()
)
gb_sorted.insert(0, "강북 순위", range(1, len(gb_sorted) + 1))

max_len_ind = max(len(gn_sorted), len(gb_sorted))
gn_sorted = gn_sorted.reindex(range(max_len_ind))
gb_sorted = gb_sorted.reindex(range(max_len_ind))

ind_table_dual = pd.DataFrame(
    {
        "강남 순위": gn_sorted["강남 순위"],
        "강남 업종": gn_sorted["업종"],
        "강남 건수": gn_sorted["강남권"],
        "강남 비중(%)": gn_sorted["강남권 비중(%)"],
        "강북 순위": gb_sorted["강북 순위"],
        "강북 업종": gb_sorted["업종"],
        "강북 건수": gb_sorted["강북권"],
        "강북 비중(%)": gb_sorted["강북권 비중(%)"],
    }
)

st.markdown("### 🔵 업종 분포 (강남/강북 비중 기준 정렬)" + title_suffix)
st.dataframe(ind_table_dual, use_container_width=True)

# -------------------------------------------------------------------------
# 🔹 광고주별 강남/강북 건수 + 비중(%), 국적, 강남/강북 각각 비중 높은 순
#    - 광고주(연락처)가 공란이고 해외본사에 값이 있으면 해외본사명을 광고주명으로 사용
# -------------------------------------------------------------------------
# 1) 광고주 표시용 컬럼 생성
region_df["광고주_표시"] = region_df["광고주(연락처)"].astype(str).str.strip()
hq_col = region_df["해외본사"].astype(str).str.strip()

# 광고주명이 공란이고 해외본사가 있는 경우 → 해외본사명을 광고주명으로 대체
mask_adv_blank = (region_df["광고주_표시"] == "") & (hq_col != "")
region_df.loc[mask_adv_blank, "광고주_표시"] = hq_col

# 2) 광고주_표시 기준으로 강남/강북 건수 집계
adv_counts = (
    region_df.groupby(["광고주_표시", "권역"])
    .size()
    .reset_index(name="건수")
)

adv_pivot = (
    adv_counts.pivot(index="광고주_표시", columns="권역", values="건수").fillna(0)
)

# 강남/강북 컬럼이 없을 수도 있으니 안전하게 보정
for col in ["강남권", "강북권"]:
    if col not in adv_pivot.columns:
        adv_pivot[col] = 0

adv_pivot["총 건수"] = adv_pivot["강남권"] + adv_pivot["강북권"]
adv_pivot["강남권 비중(%)"] = (
    adv_pivot["강남권"] / adv_pivot["총 건수"].replace(0, 1) * 100
).round(1)
adv_pivot["강북권 비중(%)"] = (
    adv_pivot["강북권"] / adv_pivot["총 건수"].replace(0, 1) * 100
).round(1)

# 3) 국적 계산 (해외본사에 값이 하나라도 있으면 '해외', 아니면 '국내')
nat_series = (
    region_df.groupby("광고주_표시")["해외본사"]
    .apply(
        lambda s: "해외"
        if (s.notna() & (s.astype(str).str.strip() != "")).any()
        else "국내"
    )
    .reset_index()
    .rename(columns={"해외본사": "국적"})
)

adv_pivot = adv_pivot.merge(nat_series, on="광고주_표시", how="left")

# 4) 강남 기준 정렬
gn_adv_sorted = (
    adv_pivot.sort_values("강남권 비중(%)", ascending=False)
    .reset_index()
)
gn_adv_sorted.insert(0, "강남 순위", range(1, len(gn_adv_sorted) + 1))

# 5) 강북 기준 정렬
gb_adv_sorted = (
    adv_pivot.sort_values("강북권 비중(%)", ascending=False)
    .reset_index()
)
gb_adv_sorted.insert(0, "강북 순위", range(1, len(gb_adv_sorted) + 1))

max_len_adv = max(len(gn_adv_sorted), len(gb_adv_sorted))
gn_adv_sorted = gn_adv_sorted.reindex(range(max_len_adv))
gb_adv_sorted = gb_adv_sorted.reindex(range(max_len_adv))

# 6) 최종 표 생성 (화면에는 '광고주'로 보이도록)
adv_table_dual = pd.DataFrame(
    {
        "강남 순위": gn_adv_sorted["강남 순위"],
        "강남 광고주": gn_adv_sorted["광고주_표시"],
        "강남 건수": gn_adv_sorted["강남권"],
        "강남 비중(%)": gn_adv_sorted["강남권 비중(%)"],
        "강남 국적": gn_adv_sorted["국적"],
        "강북 순위": gb_adv_sorted["강북 순위"],
        "강북 광고주": gb_adv_sorted["광고주_표시"],
        "강북 건수": gb_adv_sorted["강북권"],
        "강북 비중(%)": gb_adv_sorted["강북권 비중(%)"],
        "강북 국적": gb_adv_sorted["국적"],
    }
)

st.markdown("### 🔴 광고주 분포 (강남/강북 비중 기준 정렬)" + title_suffix)
st.dataframe(adv_table_dual, use_container_width=True)

# ✅ 구글시트 링크
st.markdown(
    """
🔗 [Google Sheet에서 직접 보기](https://docs.google.com/spreadsheets/d/1AFotC96rl9nz1m2BDgn2mGSm3Jo69-mcGWAquYvWEwE/edit)
"""
)
