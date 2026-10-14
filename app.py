
import streamlit as st
import pandas as pd
import calendar
from datetime import date
from io import BytesIO

# ==================================================
# 1. CẤU HÌNH ỨNG DỤNG
# ==================================================
st.set_page_config(
    page_title="Kế hoạch trả nợ vay",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 BẢNG KẾ HOẠCH TRẢ NỢ VAY")
st.write(
    "Tính tiền gốc, tiền lãi theo dư nợ thực tế, "
    "lãi suất ưu đãi và lãi suất thông thường."
)

# ==================================================
# 2. HÀM XỬ LÝ NGÀY THÁNG
# ==================================================
def cong_thang(ngay, so_thang):
    tong_thang = ngay.month - 1 + so_thang
    nam_moi = ngay.year + tong_thang // 12
    thang_moi = tong_thang % 12 + 1

    ngay_cuoi_thang = calendar.monthrange(
        nam_moi, thang_moi
    )[1]

    ngay_moi = min(ngay.day, ngay_cuoi_thang)

    return date(nam_moi, thang_moi, ngay_moi)


def ngay_thu_no_dau_tien(ngay_giai_ngan, ngay_thu_no):
    ngay_toi_da = calendar.monthrange(
        ngay_giai_ngan.year,
        ngay_giai_ngan.month
    )[1]

    ngay_du_kien = date(
        ngay_giai_ngan.year,
        ngay_giai_ngan.month,
        min(ngay_thu_no, ngay_toi_da)
    )

    if ngay_du_kien > ngay_giai_ngan:
        return ngay_du_kien

    return cong_thang(ngay_du_kien, 1)


def tinh_lai(
    ngay_bat_dau,
    ngay_ket_thuc,
    du_no,
    ls_uu_dai,
    ls_thong_thuong,
    ngay_het_uu_dai
):
    if ngay_ket_thuc <= ngay_bat_dau:
        return 0.0, 0, 0

    ngay_giao = min(ngay_ket_thuc, ngay_het_uu_dai)

    ngay_uu_dai = max(
        0,
        (ngay_giao - ngay_bat_dau).days
    ) if ngay_bat_dau < ngay_het_uu_dai else 0

    ngay_thuong = max(
        0,
        (ngay_ket_thuc - max(
            ngay_bat_dau, ngay_het_uu_dai
        )).days
    )

    lai_uu_dai = (
        du_no * (ls_uu_dai / 100)
        * ngay_uu_dai / 365
    )

    lai_thuong = (
        du_no * (ls_thong_thuong / 100)
        * ngay_thuong / 365
    )

    return (
        lai_uu_dai + lai_thuong,
        ngay_uu_dai,
        ngay_thuong
    )


# ==================================================
# 3. NHẬP THÔNG TIN KHOẢN VAY
# ==================================================
st.subheader("1. Thông tin khoản vay")

col1, col2, col3 = st.columns(3)

with col1:
    so_tien_vay = st.number_input(
        "Số tiền vay (VNĐ)",
        min_value=1_000_000,
        value=700_000_000,
        step=10_000_000,
        format="%d"
    )

    thoi_han_vay = st.number_input(
        "Thời hạn vay (tháng)",
        min_value=1,
        max_value=600,
        value=60,
        step=1
    )

with col2:
    ls_uu_dai = st.number_input(
        "Lãi suất ưu đãi (%/năm)",
        min_value=0.0,
        max_value=100.0,
        value=9.0,
        step=0.5
    )

    thoi_gian_uu_dai = st.number_input(
        "Thời gian ưu đãi (tháng)",
        min_value=0,
        max_value=int(thoi_han_vay),
        value=min(3, int(thoi_han_vay)),
        step=1
    )

with col3:
    ls_thong_thuong = st.number_input(
        "Lãi suất thông thường (%/năm)",
        min_value=0.0,
        max_value=100.0,
        value=14.0,
        step=0.5
    )

    ngay_giai_ngan = st.date_input(
        "Ngày giải ngân",
        value=date(2023, 10, 22),
        format="DD/MM/YYYY"
    )

col4, col5 = st.columns(2)

with col4:
    ngay_thu_no = st.number_input(
        "Ngày thu nợ hàng tháng",
        min_value=1,
        max_value=31,
        value=15,
        step=1
    )

with col5:
    so_ky_hien_thi = st.number_input(
        "Số kỳ muốn xem",
        min_value=1,
        max_value=int(thoi_han_vay),
        value=min(5, int(thoi_han_vay)),
        step=1
    )

st.info(
    "Gốc trả đều hằng tháng. Lãi tính theo dư nợ đầu kỳ, "
    "số ngày thực tế/365. Lãi suất được chuyển từ ưu đãi "
    "sang thông thường tại ngày hết thời gian ưu đãi."
)

# ==================================================
# 4. LẬP BẢNG TRẢ NỢ
# ==================================================
if st.button(
    "📊 LẬP BẢNG KẾ HOẠCH TRẢ NỢ",
    type="primary",
    use_container_width=True
):
    ngay_het_uu_dai = cong_thang(
        ngay_giai_ngan,
        int(thoi_gian_uu_dai)
    )

    ngay_thu_dau = ngay_thu_no_dau_tien(
        ngay_giai_ngan,
        int(ngay_thu_no)
    )

    so_ky = int(thoi_han_vay)
    tien_goc_co_so = float(so_tien_vay) / so_ky

    du_no = float(so_tien_vay)
    ngay_dau_ky = ngay_giai_ngan
    danh_sach = []

    # Tính tất cả các kỳ
    for ky in range(1, so_ky + 1):
        ngay_den_han = cong_thang(
            ngay_thu_dau,
            ky - 1
        )

        so_ngay = (
            ngay_den_han - ngay_dau_ky
        ).days

        # Trả gốc đều, kỳ cuối trả hết dư nợ
        if ky < so_ky:
            tien_goc = min(tien_goc_co_so, du_no)
        else:
            tien_goc = du_no

        tien_lai, ngay_ud, ngay_tt = tinh_lai(
            ngay_bat_dau=ngay_dau_ky,
            ngay_ket_thuc=ngay_den_han,
            du_no=du_no,
            ls_uu_dai=float(ls_uu_dai),
            ls_thong_thuong=float(ls_thong_thuong),
            ngay_het_uu_dai=ngay_het_uu_dai
        )

        tong_tra = tien_goc + tien_lai
        du_no_cuoi = max(0.0, du_no - tien_goc)

        danh_sach.append({
            "Kỳ": ky,
            "Ngày đầu kỳ": ngay_dau_ky,
            "Ngày trả nợ": ngay_den_han,
            "Số ngày tính lãi": so_ngay,
            "Dư nợ đầu kỳ (VNĐ)": round(du_no, 2),
            "Số ngày lãi ưu đãi": ngay_ud,
            "Số ngày lãi thông thường": ngay_tt,
            "Tiền gốc (VNĐ)": round(tien_goc, 2),
            "Tiền lãi (VNĐ)": round(tien_lai, 2),
            "Tổng phải trả (VNĐ)": round(tong_tra, 2),
            "Dư nợ cuối kỳ (VNĐ)": round(du_no_cuoi, 2)
        })

        du_no = du_no_cuoi
        ngay_dau_ky = ngay_den_han

    df = pd.DataFrame(danh_sach)

    # ==================================================
    # 5. TỔNG QUAN KHOẢN VAY
    # ==================================================
    tong_goc = df["Tiền gốc (VNĐ)"].sum()
    tong_lai = df["Tiền lãi (VNĐ)"].sum()
    tong_thanh_toan = df["Tổng phải trả (VNĐ)"].sum()

    st.divider()
    st.subheader("2. Tổng quan khoản vay")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Số tiền vay", f"{so_tien_vay:,.0f} VNĐ")
    c2.metric("Tổng tiền gốc", f"{tong_goc:,.0f} VNĐ")
    c3.metric("Tổng tiền lãi", f"{tong_lai:,.0f} VNĐ")
    c4.metric("Tổng phải trả", f"{tong_thanh_toan:,.0f} VNĐ")

    st.write(
        f"**Ngày giải ngân:** "
        f"{ngay_giai_ngan.strftime('%d/%m/%Y')}"
    )
    st.write(
        f"**Ngày hết ưu đãi:** "
        f"{ngay_het_uu_dai.strftime('%d/%m/%Y')}"
    )
    st.write(
        f"**Ngày thu nợ kỳ đầu:** "
        f"{ngay_thu_dau.strftime('%d/%m/%Y')}"
    )

    # ==================================================
    # 6. HIỂN THỊ BẢNG TRẢ NỢ
    # ==================================================
    st.divider()
    st.subheader(
        f"3. Chi tiết kế hoạch trả nợ "
        f"({int(so_ky_hien_thi)} kỳ được chọn)"
    )

    df_xem = df.head(int(so_ky_hien_thi)).copy()

    for cot in ["Ngày đầu kỳ", "Ngày trả nợ"]:
        df_xem[cot] = df_xem[cot].apply(
            lambda x: x.strftime("%d/%m/%Y")
        )

    st.dataframe(
        df_xem,
        use_container_width=True,
        hide_index=True
    )

    # ==================================================
    # 7. BIỂU ĐỒ DƯ NỢ
    # ==================================================
    st.subheader("4. Biểu đồ dư nợ")

    df_bieu_do = df[
        ["Kỳ", "Dư nợ cuối kỳ (VNĐ)"]
    ].set_index("Kỳ")

    st.line_chart(df_bieu_do)

    # ==================================================
    # 8. XUẤT FILE EXCEL
    # ==================================================
    st.divider()
    st.subheader("5. Tải bảng kế hoạch trả nợ")

    excel_buffer = BytesIO()

    with pd.ExcelWriter(
        excel_buffer,
        engine="openpyxl"
    ) as writer:
        df.to_excel(
            writer,
            index=False,
            sheet_name="Ke_hoach_tra_no"
        )

        df_tong_quan = pd.DataFrame({
            "Thông tin": [
                "Số tiền vay (VNĐ)",
                "Thời hạn vay (tháng)",
                "Lãi suất ưu đãi (%/năm)",
                "Thời gian ưu đãi (tháng)",
                "Lãi suất thông thường (%/năm)",
                "Ngày giải ngân",
                "Ngày thu nợ hàng tháng",
                "Ngày hết ưu đãi",
                "Tổng tiền gốc (VNĐ)",
                "Tổng tiền lãi (VNĐ)",
                "Tổng phải trả (VNĐ)"
            ],
            "Giá trị": [
                so_tien_vay,
                int(thoi_han_vay),
                ls_uu_dai,
                int(thoi_gian_uu_dai),
                ls_thong_thuong,
                ngay_giai_ngan.strftime("%d/%m/%Y"),
                int(ngay_thu_no),
                ngay_het_uu_dai.strftime("%d/%m/%Y"),
                tong_goc,
                tong_lai,
                tong_thanh_toan
            ]
        })

        df_tong_quan.to_excel(
            writer,
            index=False,
            sheet_name="Tong_quan"
        )

    st.download_button(
        label="📥 TẢI BẢNG TRẢ NỢ EXCEL",
        data=excel_buffer.getvalue(),
        file_name="ke_hoach_tra_no.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        use_container_width=True
    )

st.caption(
    "Lưu ý: Kết quả phụ thuộc vào ngày tính lãi, "
    "quy ước 365 ngày/năm và điều khoản khoản vay thực tế."
)
