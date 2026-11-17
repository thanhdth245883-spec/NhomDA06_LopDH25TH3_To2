from datetime import date, datetime
import tkinter as tk
from tkinter import messagebox
from db_connection import mo_ket_noi_co_so_du_lieu
from ui_components import (
    BANG_MAU_KHACH_SAN,
    OHopChonKhachSan,
    ONhapLieuKhachSan,
    cau_hinh_giao_dien_ttk,
    tao_bang_du_lieu,
    tao_nut_khach_san,
    xoa_du_lieu_bang,
)


def _phan_tich_ngay_bao_cao(chuoi_ngay):
    try:
        return datetime.strptime(chuoi_ngay.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def _trich_xuat_tham_so_khoi_tao(doi_tuong, doi_so_1, doi_so_2=None):
    """Hỗ trợ linh hoạt cả 2 cách gọi: (ung_dung, khung_cha) hoặc (khung_cha, duong_dan_db)."""
    if hasattr(doi_so_1, "cua_so_goc"):
        doi_tuong.cua_so_goc = doi_so_1.cua_so_goc
        doi_tuong.khung_cha = doi_so_2
        doi_tuong.duong_dan_co_so_du_lieu = getattr(
            doi_so_1, "duong_dan_co_so_du_lieu", None
        )
        for ten in (
            "nen_chinh",
            "dieu_huong_nen",
            "nhan_manh_mau",
            "van_ban_mau",
            "phu_mau",
            "the_nen",
        ):
            setattr(
                doi_tuong,
                ten,
                getattr(doi_so_1, ten, BANG_MAU_KHACH_SAN[ten]),
            )
    else:
        doi_tuong.khung_cha = doi_so_1
        doi_tuong.cua_so_goc = doi_so_1.winfo_toplevel()
        doi_tuong.duong_dan_co_so_du_lieu = doi_so_2
        for ten, gia_tri in BANG_MAU_KHACH_SAN.items():
            setattr(doi_tuong, ten, gia_tri)


def _tao_the_thong_ke(khung_cha, tieu_de, mau_nhan_manh, mau_nen_the, mau_phu):
    the = tk.Frame(
        khung_cha,
        bg=mau_nen_the,
        padx=18,
        pady=12,
        highlightthickness=1,
        highlightbackground=BANG_MAU_KHACH_SAN["vien_the"],
    )
    tk.Label(
        the,
        text=tieu_de,
        font=("Arial", 9, "bold"),
        fg=mau_phu,
        bg=mau_nen_the,
    ).pack(anchor="w")
    nhan_gia_tri = tk.Label(
        the,
        text="0",
        font=("Arial", 16, "bold"),
        fg=mau_nhan_manh,
        bg=mau_nen_the,
    )
    nhan_gia_tri.pack(anchor="w", pady=(4, 0))
    return the, nhan_gia_tri


class BieuMauBaoCao:
    """Báo cáo doanh thu & danh sách hóa đơn thanh toán."""

    def __init__(doi_tuong, doi_so_1, doi_so_2=None, khoi_tao=True):
        _trich_xuat_tham_so_khoi_tao(doi_tuong, doi_so_1, doi_so_2)
        doi_tuong.tu_khoa_tim_kiem = None

    def tao_giao_dien(doi_tuong):
        noi_dung = doi_tuong.khung_cha

        # Tiêu đề đầu trang
        dau_trang = tk.Frame(noi_dung, bg=doi_tuong.nen_chinh)
        dau_trang.pack(fill="x", pady=(0, 14))
        tk.Label(
            dau_trang,
            text="Báo cáo doanh thu & Hóa đơn",
            font=("Arial", 22, "bold"),
            fg=doi_tuong.dieu_huong_nen,
            bg=doi_tuong.nen_chinh,
        ).pack(anchor="w")
        tk.Label(
            dau_trang,
            text="Thống kê chi tiết hóa đơn thanh toán, phụ phí và tổng doanh thu theo khoảng thời gian",
            font=("Arial", 10),
            fg=doi_tuong.phu_mau,
            bg=doi_tuong.nen_chinh,
        ).pack(anchor="w", pady=(4, 0))

        # Khung bộ lọc thời gian & phương thức thanh toán
        khung_loc = tk.Frame(
            noi_dung,
            bg=doi_tuong.the_nen,
            padx=18,
            pady=14,
            highlightthickness=1,
            highlightbackground=BANG_MAU_KHACH_SAN["vien_the"],
        )
        khung_loc.pack(fill="x")

        nhan_kieu = {
            "bg": doi_tuong.the_nen,
            "fg": doi_tuong.phu_mau,
            "font": ("Arial", 9, "bold"),
        }

        hom_nay = date.today()
        dau_thang = hom_nay.replace(day=1).isoformat()

        tk.Label(khung_loc, text="Từ ngày (YYYY-MM-DD)", **nhan_kieu).grid(
            row=0, column=0, padx=(0, 12), pady=(0, 2), sticky="w"
        )
        doi_tuong.o_tu_ngay = ONhapLieuKhachSan(khung_loc)
        doi_tuong.o_tu_ngay.insert(0, dau_thang)
        doi_tuong.o_tu_ngay.grid(row=1, column=0, padx=(0, 12), sticky="ew")

        tk.Label(khung_loc, text="Đến ngày (YYYY-MM-DD)", **nhan_kieu).grid(
            row=0, column=1, padx=(0, 12), pady=(0, 2), sticky="w"
        )
        doi_tuong.o_den_ngay = ONhapLieuKhachSan(khung_loc)
        doi_tuong.o_den_ngay.insert(0, hom_nay.isoformat())
        doi_tuong.o_den_ngay.grid(row=1, column=1, padx=(0, 12), sticky="ew")

        tk.Label(khung_loc, text="Phương thức thanh toán", **nhan_kieu).grid(
            row=0, column=2, padx=(0, 12), pady=(0, 2), sticky="w"
        )
        doi_tuong.hop_phuong_thuc = OHopChonKhachSan(
            khung_loc, values=("Tất cả", "Tiền mặt", "Chuyển khoản", "Thẻ")
        )
        doi_tuong.hop_phuong_thuc.set("Tất cả")
        doi_tuong.hop_phuong_thuc.grid(row=1, column=2, padx=(0, 12), sticky="ew")

        khung_nut = tk.Frame(khung_loc, bg=doi_tuong.the_nen)
        khung_nut.grid(row=1, column=3, sticky="e")
        tao_nut_khach_san(
            khung_nut,
            "Xem báo cáo",
            doi_tuong.tai_lai_danh_sach,
            doi_tuong.dieu_huong_nen,
            padx=14,
        ).pack(side="left", padx=(0, 6))
        tao_nut_khach_san(
            khung_nut,
            "Tất cả thời gian",
            doi_tuong.xem_tat_ca_hoa_don,
            doi_tuong.nhan_manh_mau,
            padx=12,
        ).pack(side="left", padx=(0, 6))
        tao_nut_khach_san(
            khung_nut,
            "Làm mới",
            doi_tuong.dat_lai_bo_loc,
            "#475569",
            padx=12,
        ).pack(side="left")

        for cot in range(3):
            khung_loc.grid_columnconfigure(cot, weight=1)

        # Hàng thẻ tổng hợp số liệu
        khung_chi_so = tk.Frame(noi_dung, bg=doi_tuong.nen_chinh)
        khung_chi_so.pack(fill="x", pady=12)

        the_1, doi_tuong.nhan_tong_hoa_don = _tao_the_thong_ke(
            khung_chi_so,
            "SỐ HÓA ĐƠN ĐÃ LẬP",
            doi_tuong.dieu_huong_nen,
            doi_tuong.the_nen,
            doi_tuong.phu_mau,
        )
        the_1.pack(side="left", fill="x", expand=True, padx=(0, 8))

        the_2, doi_tuong.nhan_tong_tien_phong = _tao_the_thong_ke(
            khung_chi_so,
            "DOANH THU TIỀN PHÒNG",
            "#2563EB",
            doi_tuong.the_nen,
            doi_tuong.phu_mau,
        )
        the_2.pack(side="left", fill="x", expand=True, padx=4)

        the_3, doi_tuong.nhan_tong_phu_phi = _tao_the_thong_ke(
            khung_chi_so,
            "TỔNG PHỤ PHÍ",
            "#475569",
            doi_tuong.the_nen,
            doi_tuong.phu_mau,
        )
        the_3.pack(side="left", fill="x", expand=True, padx=4)

        the_4, doi_tuong.nhan_tong_doanh_thu = _tao_the_thong_ke(
            khung_chi_so,
            "TỔNG DOANH THU THỰC THU",
            doi_tuong.nhan_manh_mau,
            doi_tuong.the_nen,
            doi_tuong.phu_mau,
        )
        the_4.pack(side="left", fill="x", expand=True, padx=(8, 0))

        # Bảng chi tiết hóa đơn
        the_bang = tk.Frame(
            noi_dung,
            bg=doi_tuong.the_nen,
            padx=16,
            pady=12,
            highlightthickness=1,
            highlightbackground=BANG_MAU_KHACH_SAN["vien_the"],
        )
        the_bang.pack(fill="both", expand=True)

        doi_tuong.bang_du_lieu = tao_bang_du_lieu(
            the_bang,
            (
                "mahd",
                "datphong_id",
                "khachhang",
                "phong",
                "ngay_tt",
                "so_dem",
                "tien_phong",
                "phu_phi",
                "tong_tien",
                "phuong_thuc",
            ),
            (
                "Mã HĐ",
                "Mã ĐP",
                "Khách hàng",
                "Phòng",
                "Ngày thanh toán",
                "Số đêm",
                "Tiền phòng",
                "Phụ phí",
                "Tổng thanh toán",
                "Phương thức",
            ),
            (65, 65, 180, 120, 115, 65, 115, 95, 125, 110),
            ("center", "center", "w", "w", "center", "center", "e", "e", "e", "center"),
            mau_nen=doi_tuong.the_nen,
        )

        doi_tuong.xem_tat_ca_hoa_don()
        return noi_dung

    def dat_lai_bo_loc(doi_tuong):
        hom_nay = date.today()
        doi_tuong.o_tu_ngay.delete(0, tk.END)
        doi_tuong.o_tu_ngay.insert(0, hom_nay.replace(day=1).isoformat())
        doi_tuong.o_den_ngay.delete(0, tk.END)
        doi_tuong.o_den_ngay.insert(0, hom_nay.isoformat())
        doi_tuong.hop_phuong_thuc.set("Tất cả")
        doi_tuong.tai_lai_danh_sach()

    def xem_tat_ca_hoa_don(doi_tuong):
        doi_tuong.o_tu_ngay.delete(0, tk.END)
        doi_tuong.o_den_ngay.delete(0, tk.END)
        doi_tuong.hop_phuong_thuc.set("Tất cả")
        doi_tuong.tai_lai_danh_sach()

    def tai_lai_danh_sach(doi_tuong):
        tu_ngay_str = doi_tuong.o_tu_ngay.get().strip()
        den_ngay_str = doi_tuong.o_den_ngay.get().strip()
        phuong_thuc = doi_tuong.hop_phuong_thuc.get()

        dieu_kien = []
        tham_so = []

        if tu_ngay_str:
            tu_ngay = _phan_tich_ngay_bao_cao(tu_ngay_str)
            if tu_ngay is None:
                messagebox.showwarning(
                    "Sai định dạng ngày",
                    "Trường 'Từ ngày' phải có định dạng YYYY-MM-DD.",
                    parent=doi_tuong.cua_so_goc,
                )
                return
            dieu_kien.append("hd.ngay_thanh_toan >= ?")
            tham_so.append(tu_ngay_str)

        if den_ngay_str:
            den_ngay = _phan_tich_ngay_bao_cao(den_ngay_str)
            if den_ngay is None:
                messagebox.showwarning(
                    "Sai định dạng ngày",
                    "Trường 'Đến ngày' phải có định dạng YYYY-MM-DD.",
                    parent=doi_tuong.cua_so_goc,
                )
                return
            dieu_kien.append("hd.ngay_thanh_toan <= ?")
            tham_so.append(den_ngay_str)

        if tu_ngay_str and den_ngay_str and tu_ngay_str > den_ngay_str:
            messagebox.showwarning(
                "Khoảng ngày không hợp lệ",
                "'Từ ngày' không được lớn hơn 'Đến ngày'.",
                parent=doi_tuong.cua_so_goc,
            )
            return

        if phuong_thuc and phuong_thuc != "Tất cả":
            dieu_kien.append("hd.phuong_thuc = ?")
            tham_so.append(phuong_thuc)

        menh_de_where = ("WHERE " + " AND ".join(dieu_kien)) if dieu_kien else ""

        xoa_du_lieu_bang(doi_tuong.bang_du_lieu)
        with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
            cac_dong = ket_noi.execute(
                f"""
                SELECT
                    hd.id,
                    hd.datphong_id,
                    kh.makh || ' - ' || kh.hoten AS khachhang,
                    p.maphong || ' - ' || p.tenphong AS phong,
                    hd.ngay_thanh_toan,
                    hd.so_dem,
                    hd.tien_phong,
                    hd.phu_phi,
                    hd.tong_tien,
                    hd.phuong_thuc
                FROM hoa_don hd
                JOIN datphong dp ON dp.id = hd.datphong_id
                JOIN khachhang kh ON kh.makh = dp.makh
                JOIN phong p ON p.maphong = dp.maphong
                {menh_de_where}
                ORDER BY hd.ngay_thanh_toan DESC, hd.id DESC
                """,
                tham_so,
            ).fetchall()

        tong_tien_phong = 0
        tong_phu_phi = 0
        tong_doanh_thu = 0

        for chi_so, dong in enumerate(cac_dong):
            nhan_dong = "dong_chan" if chi_so % 2 == 0 else "dong_le"
            tong_tien_phong += dong["tien_phong"]
            tong_phu_phi += dong["phu_phi"]
            tong_doanh_thu += dong["tong_tien"]

            doi_tuong.bang_du_lieu.insert(
                "",
                tk.END,
                values=(
                    f"HD{dong['id']:03d}",
                    f"#{dong['datphong_id']}",
                    dong["khachhang"],
                    dong["phong"],
                    dong["ngay_thanh_toan"],
                    f"{dong['so_dem']} đêm",
                    f"{dong['tien_phong']:,.0f} đ",
                    f"{dong['phu_phi']:,.0f} đ",
                    f"{dong['tong_tien']:,.0f} đ",
                    dong["phuong_thuc"],
                ),
                tags=(nhan_dong,),
            )

        doi_tuong.nhan_tong_hoa_don.config(text=f"{len(cac_dong)} hóa đơn")
        doi_tuong.nhan_tong_tien_phong.config(text=f"{tong_tien_phong:,.0f} đ")
        doi_tuong.nhan_tong_phu_phi.config(text=f"{tong_phu_phi:,.0f} đ")
        doi_tuong.nhan_tong_doanh_thu.config(text=f"{tong_doanh_thu:,.0f} đ")


class BieuMauBaoCaoCongSuatPhong:
    """Báo cáo tình trạng phòng hiện tại & hiệu suất khai thác từng phòng."""

    def __init__(doi_tuong, doi_so_1, doi_so_2=None, khoi_tao=True):
        _trich_xuat_tham_so_khoi_tao(doi_tuong, doi_so_1, doi_so_2)

    def tao_giao_dien(doi_tuong):
        noi_dung = doi_tuong.khung_cha

        # Tiêu đề đầu trang
        dau_trang = tk.Frame(noi_dung, bg=doi_tuong.nen_chinh)
        dau_trang.pack(fill="x", pady=(0, 14))
        tk.Label(
            dau_trang,
            text="Báo cáo tình trạng & Công suất phòng",
            font=("Arial", 22, "bold"),
            fg=doi_tuong.dieu_huong_nen,
            bg=doi_tuong.nen_chinh,
        ).pack(anchor="w")
        tk.Label(
            dau_trang,
            text="Theo dõi tỷ lệ lấp đầy phòng, số lượt khai thác và doanh thu mang lại trên từng phòng",
            font=("Arial", 10),
            fg=doi_tuong.phu_mau,
            bg=doi_tuong.nen_chinh,
        ).pack(anchor="w", pady=(4, 0))

        # Hàng thẻ chỉ số tổng quan
        khung_chi_so = tk.Frame(noi_dung, bg=doi_tuong.nen_chinh)
        khung_chi_so.pack(fill="x", pady=(0, 12))

        the_1, doi_tuong.nhan_tong_so_phong = _tao_the_thong_ke(
            khung_chi_so,
            "TỔNG SỐ PHÒNG",
            doi_tuong.dieu_huong_nen,
            doi_tuong.the_nen,
            doi_tuong.phu_mau,
        )
        the_1.pack(side="left", fill="x", expand=True, padx=(0, 8))

        the_2, doi_tuong.nhan_phong_dang_o = _tao_the_thong_ke(
            khung_chi_so,
            "ĐANG CÓ KHÁCH Ở",
            "#B91C1C",
            doi_tuong.the_nen,
            doi_tuong.phu_mau,
        )
        the_2.pack(side="left", fill="x", expand=True, padx=4)

        the_3, doi_tuong.nhan_phong_da_dat = _tao_the_thong_ke(
            khung_chi_so,
            "ĐÃ ĐẶT TRƯỚC",
            "#2563EB",
            doi_tuong.the_nen,
            doi_tuong.phu_mau,
        )
        the_3.pack(side="left", fill="x", expand=True, padx=4)

        the_4, doi_tuong.nhan_phong_trong = _tao_the_thong_ke(
            khung_chi_so,
            "PHÒNG TRỐNG SẴN SÀNG",
            "#15803D",
            doi_tuong.the_nen,
            doi_tuong.phu_mau,
        )
        the_4.pack(side="left", fill="x", expand=True, padx=(8, 0))

        # Khung lọc tình trạng & bảng thống kê công suất
        the_bang = tk.Frame(
            noi_dung,
            bg=doi_tuong.the_nen,
            padx=16,
            pady=12,
            highlightthickness=1,
            highlightbackground=BANG_MAU_KHACH_SAN["vien_the"],
        )
        the_bang.pack(fill="both", expand=True)

        khung_loc = tk.Frame(the_bang, bg=doi_tuong.the_nen)
        khung_loc.pack(fill="x", pady=(0, 10))

        tk.Label(
            khung_loc,
            text="Tình trạng hiện tại:",
            bg=doi_tuong.the_nen,
            fg=doi_tuong.van_ban_mau,
            font=("Arial", 9, "bold"),
        ).pack(side="left", padx=(0, 8))

        doi_tuong.hop_loc_tinh_trang = OHopChonKhachSan(
            khung_loc,
            values=("Tất cả", "Đang có khách ở", "Đã đặt trước", "Phòng trống"),
            width=18,
        )
        doi_tuong.hop_loc_tinh_trang.set("Tất cả")
        doi_tuong.hop_loc_tinh_trang.pack(side="left", padx=(0, 10))
        doi_tuong.hop_loc_tinh_trang.bind(
            "<<ComboboxSelected>>", lambda _: doi_tuong.tai_lai_danh_sach()
        )

        tao_nut_khach_san(
            khung_loc,
            "Làm mới số liệu",
            doi_tuong.tai_lai_danh_sach,
            doi_tuong.dieu_huong_nen,
            padx=12,
        ).pack(side="left")

        doi_tuong.bang_du_lieu = tao_bang_du_lieu(
            the_bang,
            (
                "maphong",
                "tenphong",
                "tenloai",
                "giaphong",
                "tinhtrang",
                "so_luot_dat",
                "tong_dem",
                "doanh_thu",
            ),
            (
                "Mã phòng",
                "Tên phòng",
                "Loại phòng",
                "Giá niêm yết",
                "Tình trạng hiện tại",
                "Tổng lượt đặt",
                "Tổng đêm bán",
                "Doanh thu phòng",
            ),
            (95, 160, 190, 125, 145, 105, 105, 145),
            ("center", "w", "w", "e", "center", "center", "center", "e"),
            mau_nen=doi_tuong.the_nen,
        )

        doi_tuong.tai_lai_danh_sach()
        return noi_dung

    def tai_lai_danh_sach(doi_tuong):
        xoa_du_lieu_bang(doi_tuong.bang_du_lieu)
        loc_tinh_trang = doi_tuong.hop_loc_tinh_trang.get()

        with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
            cac_dong = ket_noi.execute(
                """
                SELECT
                    p.maphong,
                    p.tenphong,
                    lp.tenloai,
                    lp.giaphong,
                    CASE
                        WHEN EXISTS (
                            SELECT 1 FROM datphong dp1
                            WHERE dp1.maphong = p.maphong AND dp1.trangthai = 'Đang ở'
                        ) THEN 'Đang có khách ở'
                        WHEN EXISTS (
                            SELECT 1 FROM datphong dp2
                            WHERE dp2.maphong = p.maphong AND dp2.trangthai = 'Đã đặt'
                        ) THEN 'Đã đặt trước'
                        ELSE 'Phòng trống'
                    END AS tinhtrang,
                    COUNT(CASE WHEN dp.trangthai != 'Đã hủy' THEN dp.id END) AS so_luot_dat,
                    COALESCE(SUM(hd.so_dem), 0) AS tong_dem,
                    COALESCE(SUM(hd.tong_tien), 0) AS doanh_thu
                FROM phong p
                JOIN loaiphong lp ON lp.maloai = p.maloai
                LEFT JOIN datphong dp ON dp.maphong = p.maphong
                LEFT JOIN hoa_don hd ON hd.datphong_id = dp.id
                GROUP BY p.maphong, p.tenphong, lp.tenloai, lp.giaphong
                ORDER BY p.maphong
                """
            ).fetchall()

        tong_phong = len(cac_dong)
        so_dang_o = sum(1 for d in cac_dong if d["tinhtrang"] == "Đang có khách ở")
        so_da_dat = sum(1 for d in cac_dong if d["tinhtrang"] == "Đã đặt trước")
        so_phong_trong = sum(1 for d in cac_dong if d["tinhtrang"] == "Phòng trống")

        doi_tuong.nhan_tong_so_phong.config(text=f"{tong_phong} phòng")
        doi_tuong.nhan_phong_dang_o.config(text=f"{so_dang_o} phòng")
        doi_tuong.nhan_phong_da_dat.config(text=f"{so_da_dat} phòng")
        doi_tuong.nhan_phong_trong.config(text=f"{so_phong_trong} phòng")

        chi_so_hien_thi = 0
        for dong in cac_dong:
            if loc_tinh_trang != "Tất cả" and dong["tinhtrang"] != loc_tinh_trang:
                continue
            nhan_dong = "dong_chan" if chi_so_hien_thi % 2 == 0 else "dong_le"
            chi_so_hien_thi += 1
            doi_tuong.bang_du_lieu.insert(
                "",
                tk.END,
                values=(
                    dong["maphong"],
                    dong["tenphong"],
                    dong["tenloai"],
                    f"{dong['giaphong']:,.0f} đ",
                    dong["tinhtrang"],
                    f"{dong['so_luot_dat']} lượt",
                    f"{dong['tong_dem']} đêm",
                    f"{dong['doanh_thu']:,.0f} đ",
                ),
                tags=(nhan_dong,),
            )


class BieuMauBaoCaoKhachHang:
    """Báo cáo danh sách khách lưu trú & lịch sử chi tiêu của khách hàng."""

    def __init__(doi_tuong, doi_so_1, doi_so_2=None, khoi_tao=True):
        _trich_xuat_tham_so_khoi_tao(doi_tuong, doi_so_1, doi_so_2)

    def tao_giao_dien(doi_tuong):
        noi_dung = doi_tuong.khung_cha

        # Tiêu đề đầu trang
        dau_trang = tk.Frame(noi_dung, bg=doi_tuong.nen_chinh)
        dau_trang.pack(fill="x", pady=(0, 14))
        tk.Label(
            dau_trang,
            text="Báo cáo danh sách khách lưu trú",
            font=("Arial", 22, "bold"),
            fg=doi_tuong.dieu_huong_nen,
            bg=doi_tuong.nen_chinh,
        ).pack(anchor="w")
        tk.Label(
            dau_trang,
            text="Thống kê tần suất lưu trú, số đêm ở và tổng chi tiêu của từng khách hàng tại THANHVY Hotel",
            font=("Arial", 10),
            fg=doi_tuong.phu_mau,
            bg=doi_tuong.nen_chinh,
        ).pack(anchor="w", pady=(4, 0))

        # Khung tìm kiếm & bảng thống kê khách hàng
        the_bang = tk.Frame(
            noi_dung,
            bg=doi_tuong.the_nen,
            padx=16,
            pady=13,
            highlightthickness=1,
            highlightbackground=BANG_MAU_KHACH_SAN["vien_the"],
        )
        the_bang.pack(fill="both", expand=True)

        khung_tim = tk.Frame(the_bang, bg=doi_tuong.the_nen)
        khung_tim.pack(fill="x", pady=(0, 10))

        doi_tuong.tu_khoa_tim_kiem = tk.StringVar()
        o_tim = ONhapLieuKhachSan(khung_tim, textvariable=doi_tuong.tu_khoa_tim_kiem)
        o_tim.pack(side="left", fill="x", expand=True)
        o_tim.bind("<Return>", lambda _: doi_tuong.tai_lai_danh_sach())

        tao_nut_khach_san(
            khung_tim,
            "Tìm khách hàng",
            doi_tuong.tai_lai_danh_sach,
            doi_tuong.dieu_huong_nen,
            padx=12,
        ).pack(side="left", padx=(8, 4))
        tao_nut_khach_san(
            khung_tim,
            "Làm mới",
            lambda: (
                doi_tuong.tu_khoa_tim_kiem.set(""),
                doi_tuong.tai_lai_danh_sach(),
            ),
            "#475569",
            padx=12,
        ).pack(side="left", padx=4)

        doi_tuong.bang_du_lieu = tao_bang_du_lieu(
            the_bang,
            (
                "makh",
                "hoten",
                "cccd",
                "sodt",
                "gioitinh",
                "so_lan_dat",
                "tong_dem",
                "tong_chi_tieu",
            ),
            (
                "Mã KH",
                "Họ và tên",
                "CCCD/CMND",
                "Số điện thoại",
                "Giới tính",
                "Số lần đặt",
                "Tổng đêm ở",
                "Tổng chi tiêu",
            ),
            (95, 195, 135, 125, 85, 95, 95, 145),
            ("center", "w", "center", "center", "center", "center", "center", "e"),
            mau_nen=doi_tuong.the_nen,
        )

        doi_tuong.tai_lai_danh_sach()
        return noi_dung

    def tai_lai_danh_sach(doi_tuong):
        xoa_du_lieu_bang(doi_tuong.bang_du_lieu)
        tu_khoa = doi_tuong.tu_khoa_tim_kiem.get().strip()

        dieu_kien = ""
        tham_so = []
        if tu_khoa:
            dieu_kien = "WHERE kh.makh LIKE ? OR kh.hoten LIKE ? OR kh.cccd LIKE ? OR kh.sodt LIKE ?"
            mau = f"%{tu_khoa}%"
            tham_so = [mau, mau, mau, mau]

        with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
            cac_dong = ket_noi.execute(
                f"""
                SELECT
                    kh.makh,
                    kh.hoten,
                    kh.cccd,
                    kh.sodt,
                    kh.gioitinh,
                    COUNT(CASE WHEN dp.trangthai != 'Đã hủy' THEN dp.id END) AS so_lan_dat,
                    COALESCE(SUM(hd.so_dem), 0) AS tong_dem,
                    COALESCE(SUM(hd.tong_tien), 0) AS tong_chi_tieu
                FROM khachhang kh
                LEFT JOIN datphong dp ON dp.makh = kh.makh
                LEFT JOIN hoa_don hd ON hd.datphong_id = dp.id
                {dieu_kien}
                GROUP BY kh.makh, kh.hoten, kh.cccd, kh.sodt, kh.gioitinh
                ORDER BY tong_chi_tieu DESC, kh.makh ASC
                """,
                tham_so,
            ).fetchall()

        for chi_so, dong in enumerate(cac_dong):
            nhan_dong = "dong_chan" if chi_so % 2 == 0 else "dong_le"
            doi_tuong.bang_du_lieu.insert(
                "",
                tk.END,
                values=(
                    dong["makh"],
                    dong["hoten"],
                    dong["cccd"],
                    dong["sodt"] or "",
                    dong["gioitinh"] or "",
                    f"{dong['so_lan_dat']} lần",
                    f"{dong['tong_dem']} đêm",
                    f"{dong['tong_chi_tieu']:,.0f} đ",
                ),
                tags=(nhan_dong,),
            )


if __name__ == "__main__":
    cua_so = tk.Tk()
    cua_so.title("Báo cáo doanh thu - Aurelia Hotel")
    cua_so.geometry("1080x680")
    cua_so.configure(bg=BANG_MAU_KHACH_SAN["nen_chinh"])
    cau_hinh_giao_dien_ttk(cua_so)

    khung = tk.Frame(cua_so, bg=BANG_MAU_KHACH_SAN["nen_chinh"], padx=16, pady=16)
    khung.pack(fill="both", expand=True)
    BieuMauBaoCao(khung, "QLKS.db", khoi_tao=False).tao_giao_dien()
    cua_so.mainloop()