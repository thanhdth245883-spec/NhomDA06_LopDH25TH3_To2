import sqlite3
import tkinter as tk
from datetime import datetime
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


def _chuan_hoa_bang_dich_vu(ket_noi):
    """Đảm bảo bảng dichvu và sudungdichvu tồn tại và có dữ liệu mẫu."""
    ket_noi.execute(
        """
        CREATE TABLE IF NOT EXISTS dichvu (
            madv TEXT PRIMARY KEY,
            tendv TEXT NOT NULL,
            dongia REAL NOT NULL DEFAULT 0,
            donvitinh TEXT DEFAULT 'Lần'
        )
        """
    )
    ket_noi.execute(
        """
        CREATE TABLE IF NOT EXISTS sudungdichvu (
            masddv TEXT PRIMARY KEY,
            madat TEXT NOT NULL,
            madv TEXT NOT NULL,
            soluong INTEGER NOT NULL DEFAULT 1,
            thanhtien REAL NOT NULL DEFAULT 0,
            ngaysudung TEXT,
            ghichu TEXT
        )
        """
    )

    so_dv = ket_noi.execute("SELECT COUNT(*) FROM dichvu").fetchone()[0]
    if so_dv == 0:
        dich_vu_mau = [
            ("DV01", "Ăn sáng Buffet", 150000, "Suất"),
            ("DV02", "Giặt ủi quần áo", 80000, "Kg"),
            ("DV03", "Đưa đón sân bay", 350000, "Chuyến"),
            ("DV04", "Spa & Massage thư giãn", 450000, "Gói"),
            ("DV05", "Nước suối & Minibar", 50000, "Combo"),
            ("DV06", "Thuê xe máy tham quan", 180000, "Ngày"),
        ]
        ket_noi.executemany(
            "INSERT INTO dichvu (madv, tendv, dongia, donvitinh) VALUES (?, ?, ?, ?)",
            dich_vu_mau,
        )


def _lay_ten_cot_thuc_te(ket_noi):
    """Tự động nhận diện tên cột thực tế trong các bảng datphong, khachhang, dichvu."""
    cot_dp = [r[1] for r in ket_noi.execute("PRAGMA table_info(datphong)").fetchall()]
    khoa_dp = next(
        (
            c
            for c in cot_dp
            if c.lower() in ("madat", "madp", "madatphong", "ma_dat", "ma_dp", "id")
        ),
        cot_dp[0] if cot_dp else "madat",
    )
    cot_phong_dp = next(
        (c for c in cot_dp if c.lower() in ("maphong", "ma_phong", "sophong")),
        None,
    )
    cot_makh_dp = next(
        (c for c in cot_dp if c.lower() in ("makh", "ma_kh", "makhachhang")),
        None,
    )

    cot_kh = [r[1] for r in ket_noi.execute("PRAGMA table_info(khachhang)").fetchall()]
    khoa_kh = next(
        (c for c in cot_kh if c.lower() in ("makh", "ma_kh", "makhachhang", "id")),
        cot_kh[0] if cot_kh else "makh",
    )
    ten_kh = next(
        (c for c in cot_kh if c.lower() in ("hoten", "tenkh", "ho_ten", "ten")),
        None,
    )

    cot_dv = [r[1] for r in ket_noi.execute("PRAGMA table_info(dichvu)").fetchall()]
    khoa_dv = next(
        (c for c in cot_dv if c.lower() in ("madv", "ma_dv", "madichvu", "id")),
        cot_dv[0] if cot_dv else "madv",
    )
    ten_dv = next(
        (c for c in cot_dv if c.lower() in ("tendv", "ten_dv", "tendichvu", "ten")),
        "tendv",
    )
    gia_dv = next(
        (c for c in cot_dv if c.lower() in ("dongia", "giadv", "gia", "don_gia")),
        "dongia",
    )

    return {
        "co_dp": bool(cot_dp),
        "khoa_dp": khoa_dp,
        "cot_phong_dp": cot_phong_dp,
        "cot_makh_dp": cot_makh_dp,
        "co_kh": bool(cot_kh),
        "khoa_kh": khoa_kh,
        "ten_kh": ten_kh,
        "khoa_dv": khoa_dv,
        "ten_dv": ten_dv,
        "gia_dv": gia_dv,
    }


class BieuMauSuDungDichVu:
    def __init__(doi_tuong, ung_dung, khung_cha):
        doi_tuong.ung_dung = ung_dung
        doi_tuong.cua_so_goc = ung_dung.cua_so_goc
        doi_tuong.duong_dan_co_so_du_lieu = getattr(
            ung_dung, "duong_dan_co_so_du_lieu", None
        )
        doi_tuong.khung_cha = khung_cha
        doi_tuong.ban_do_dat_phong = {}
        doi_tuong.ban_do_dich_vu = {}

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
                getattr(ung_dung, ten, BANG_MAU_KHACH_SAN[ten]),
            )

    def tao_giao_dien(doi_tuong):
        noi_dung = doi_tuong.khung_cha

        # Tiêu đề đầu trang
        dau_trang = tk.Frame(noi_dung, bg=doi_tuong.nen_chinh)
        dau_trang.pack(fill="x", pady=(0, 12))
        tk.Label(
            dau_trang,
            text="Quản lý sử dụng dịch vụ",
            font=("Arial", 22, "bold"),
            fg=doi_tuong.dieu_huong_nen,
            bg=doi_tuong.nen_chinh,
        ).pack(anchor="w")
        tk.Label(
            dau_trang,
            text="Ghi nhận dịch vụ phát sinh theo phiếu đặt phòng và tự động tính tổng phụ thu",
            font=("Arial", 10),
            fg=doi_tuong.phu_mau,
            bg=doi_tuong.nen_chinh,
        ).pack(anchor="w", pady=(4, 0))

        # Khung nhập thông tin sử dụng dịch vụ
        khung_nhap = tk.Frame(
            noi_dung,
            bg=doi_tuong.the_nen,
            padx=20,
            pady=14,
            highlightthickness=1,
            highlightbackground=BANG_MAU_KHACH_SAN["vien_the"],
        )
        khung_nhap.pack(fill="x")

        nhan_kieu = {
            "bg": doi_tuong.the_nen,
            "fg": doi_tuong.phu_mau,
            "font": ("Arial", 9, "bold"),
        }

        # Dòng 1: Mã sử dụng DV, Phiếu đặt phòng, Dịch vụ
        tk.Label(khung_nhap, text="Mã phiếu dịch vụ", **nhan_kieu).grid(
            row=0, column=0, padx=(0, 14), pady=(0, 2), sticky="w"
        )
        doi_tuong.o_ma_sddv = ONhapLieuKhachSan(khung_nhap)
        doi_tuong.o_ma_sddv.grid(row=1, column=0, padx=(0, 14), pady=(0, 8), sticky="ew")

        tk.Label(khung_nhap, text="Phiếu đặt phòng / Khách đang ở", **nhan_kieu).grid(
            row=0, column=1, padx=(0, 14), pady=(0, 2), sticky="w"
        )
        doi_tuong.hop_dat_phong = OHopChonKhachSan(khung_nhap)
        doi_tuong.hop_dat_phong.grid(
            row=1, column=1, padx=(0, 14), pady=(0, 8), sticky="ew"
        )

        tk.Label(khung_nhap, text="Dịch vụ sử dụng", **nhan_kieu).grid(
            row=0, column=2, pady=(0, 2), sticky="w"
        )
        doi_tuong.hop_dich_vu = OHopChonKhachSan(khung_nhap)
        doi_tuong.hop_dich_vu.grid(row=1, column=2, pady=(0, 8), sticky="ew")
        doi_tuong.hop_dich_vu.bind(
            "<<ComboboxSelected>>", lambda _: doi_tuong._cap_nhat_thanh_tien_tam_tinh()
        )

        # Dòng 2: Số lượng, Ngày sử dụng, Ghi chú & Thành tiền tạm tính
        tk.Label(khung_nhap, text="Số lượng", **nhan_kieu).grid(
            row=2, column=0, padx=(0, 14), pady=(2, 2), sticky="w"
        )
        doi_tuong.o_so_luong = ONhapLieuKhachSan(khung_nhap)
        doi_tuong.o_so_luong.insert(0, "1")
        doi_tuong.o_so_luong.grid(
            row=3, column=0, padx=(0, 14), pady=(0, 4), sticky="ew"
        )
        doi_tuong.o_so_luong.bind(
            "<KeyRelease>", lambda _: doi_tuong._cap_nhat_thanh_tien_tam_tinh()
        )

        tk.Label(khung_nhap, text="Ngày sử dụng (YYYY-MM-DD)", **nhan_kieu).grid(
            row=2, column=1, padx=(0, 14), pady=(2, 2), sticky="w"
        )
        doi_tuong.o_ngay_su_dung = ONhapLieuKhachSan(khung_nhap)
        doi_tuong.o_ngay_su_dung.insert(0, datetime.now().strftime("%Y-%m-%d"))
        doi_tuong.o_ngay_su_dung.grid(
            row=3, column=1, padx=(0, 14), pady=(0, 4), sticky="ew"
        )

        tk.Label(khung_nhap, text="Ghi chú / Thành tiền dự kiến", **nhan_kieu).grid(
            row=2, column=2, pady=(2, 2), sticky="w"
        )
        khung_phu = tk.Frame(khung_nhap, bg=doi_tuong.the_nen)
        khung_phu.grid(row=3, column=2, pady=(0, 4), sticky="ew")

        doi_tuong.o_ghi_chu = ONhapLieuKhachSan(khung_phu)
        doi_tuong.o_ghi_chu.pack(side="left", fill="x", expand=True)

        doi_tuong.nhan_thanh_tien = tk.Label(
            khung_phu,
            text="0 đ",
            font=("Arial", 10, "bold"),
            fg=doi_tuong.nhan_manh_mau,
            bg=doi_tuong.the_nen,
            padx=10,
        )
        doi_tuong.nhan_thanh_tien.pack(side="right")

        for cot in range(3):
            khung_nhap.grid_columnconfigure(cot, weight=1)

        # Thanh nút chức năng CRUD
        cac_thao_tac = tk.Frame(noi_dung, bg=doi_tuong.nen_chinh)
        cac_thao_tac.pack(fill="x", pady=12)
        tao_nut_khach_san(
            cac_thao_tac,
            "Thêm dịch vụ",
            doi_tuong.them_su_dung_dich_vu,
            doi_tuong.dieu_huong_nen,
        ).pack(side="left", padx=(0, 8))
        tao_nut_khach_san(
            cac_thao_tac,
            "Cập nhật",
            doi_tuong.sua_su_dung_dich_vu,
            doi_tuong.nhan_manh_mau,
        ).pack(side="left", padx=4)
        tao_nut_khach_san(
            cac_thao_tac,
            "Xóa dịch vụ",
            doi_tuong.xoa_su_dung_dich_vu,
            "#B91C1C",
        ).pack(side="left", padx=4)
        tao_nut_khach_san(
            cac_thao_tac,
            "Làm mới ô nhập",
            doi_tuong.xoa_o_nhap,
            "#52615D",
        ).pack(side="left", padx=4)

        doi_tuong.nhan_tong_cong = tk.Label(
            cac_thao_tac,
            text="Tổng tiền dịch vụ: 0 VNĐ",
            font=("Arial", 11, "bold"),
            fg=doi_tuong.dieu_huong_nen,
            bg=doi_tuong.nen_chinh,
        )
        doi_tuong.nhan_tong_cong.pack(side="right")

        # Khung tìm kiếm & bảng danh sách sử dụng dịch vụ
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
        o_tim.bind("<Return>", lambda _: doi_tuong.tim_kiem_su_dung_dich_vu())

        tao_nut_khach_san(
            khung_tim,
            "Tìm kiếm",
            doi_tuong.tim_kiem_su_dung_dich_vu,
            doi_tuong.dieu_huong_nen,
            padx=12,
        ).pack(side="left", padx=(8, 4))
        tao_nut_khach_san(
            khung_tim,
            "Tải lại",
            lambda: (
                doi_tuong.tu_khoa_tim_kiem.set(""),
                doi_tuong.tai_du_lieu_su_dung_dich_vu(),
            ),
            "#475569",
            padx=12,
        ).pack(side="left", padx=4)

        doi_tuong.bang_du_lieu = tao_bang_du_lieu(
            the_bang,
            ("masddv", "madat", "khachhang", "tendv", "soluong", "thanhtien", "ngaysudung", "ghichu"),
            ("Mã SDDV", "Mã đặt", "Khách hàng / Phòng", "Dịch vụ", "SL", "Thành tiền", "Ngày SD", "Ghi chú"),
            (95, 95, 200, 180, 60, 130, 110, 150),
            ("center", "center", "w", "w", "center", "e", "center", "w"),
            mau_nen=doi_tuong.the_nen,
        )
        doi_tuong.bang_du_lieu.bind("<<TreeviewSelect>>", doi_tuong.chon_dong_dich_vu)

        doi_tuong.tai_du_lieu_su_dung_dich_vu()
        return noi_dung

    def _tai_danh_muc_combobox(doi_tuong, ket_noi, cot):
        """Nạp danh sách phiếu đặt phòng và danh sách dịch vụ vào Combobox."""
        ds_dv = ket_noi.execute(
            f"SELECT {cot['khoa_dv']} AS madv, {cot['ten_dv']} AS tendv, {cot['gia_dv']} AS dongia FROM dichvu ORDER BY {cot['khoa_dv']}"
        ).fetchall()
        doi_tuong.ban_do_dich_vu.clear()
        hien_thi_dv = []
        for dv in ds_dv:
            nhan = f"{dv['madv']} - {dv['tendv']} ({float(dv['dongia'] or 0):,.0f} đ)"
            doi_tuong.ban_do_dich_vu[nhan] = (dv["madv"], float(dv["dongia"] or 0))
            hien_thi_dv.append(nhan)
        doi_tuong.hop_dich_vu["values"] = hien_thi_dv
        if hien_thi_dv and not doi_tuong.hop_dich_vu.get():
            doi_tuong.hop_dich_vu.set(hien_thi_dv[0])

        # Nạp phiếu đặt phòng theo đúng cột thực tế của datphong
        doi_tuong.ban_do_dat_phong.clear()
        hien_thi_dp = []
        if cot["co_dp"]:
            bieu_thuc_phong = (
                f"COALESCE(dp.{cot['cot_phong_dp']}, '')"
                if cot["cot_phong_dp"]
                else "''"
            )
            if cot["co_kh"] and cot["cot_makh_dp"] and cot["ten_kh"]:
                ds_dp = ket_noi.execute(
                    f"""
                    SELECT dp.{cot['khoa_dp']} AS madat,
                           {bieu_thuc_phong} AS maphong,
                           COALESCE(kh.{cot['ten_kh']}, 'Khách lẻ') AS hoten
                    FROM datphong dp
                    LEFT JOIN khachhang kh ON dp.{cot['cot_makh_dp']} = kh.{cot['khoa_kh']}
                    ORDER BY dp.{cot['khoa_dp']} DESC
                    """
                ).fetchall()
            else:
                ds_dp = ket_noi.execute(
                    f"""
                    SELECT dp.{cot['khoa_dp']} AS madat,
                           {bieu_thuc_phong} AS maphong,
                           '' AS hoten
                    FROM datphong dp
                    ORDER BY dp.{cot['khoa_dp']} DESC
                    """
                ).fetchall()

            for dp in ds_dp:
                phong_txt = f" - Phòng {dp['maphong']}" if dp["maphong"] else ""
                khach_txt = f" ({dp['hoten']})" if dp["hoten"] else ""
                nhan = f"{dp['madat']}{phong_txt}{khach_txt}"
                doi_tuong.ban_do_dat_phong[nhan] = str(dp["madat"])
                hien_thi_dp.append(nhan)

        doi_tuong.hop_dat_phong["values"] = hien_thi_dp
        if hien_thi_dp and not doi_tuong.hop_dat_phong.get():
            doi_tuong.hop_dat_phong.set(hien_thi_dp[0])

        doi_tuong._cap_nhat_thanh_tien_tam_tinh()

    def _cap_nhat_thanh_tien_tam_tinh(doi_tuong):
        dv_chon = doi_tuong.hop_dich_vu.get()
        thong_tin_dv = doi_tuong.ban_do_dich_vu.get(dv_chon)
        try:
            so_luong = int(doi_tuong.o_so_luong.get().strip() or "0")
        except ValueError:
            so_luong = 0
        don_gia = thong_tin_dv[1] if thong_tin_dv else 0
        tong = max(0, so_luong) * don_gia
        doi_tuong.nhan_thanh_tien.configure(text=f"{tong:,.0f} đ")

    def _sinh_ma_sddv_tu_dong(doi_tuong, ket_noi):
        dong = ket_noi.execute(
            "SELECT masddv FROM sudungdichvu ORDER BY masddv DESC LIMIT 1"
        ).fetchone()
        if not dong:
            return "SD01"
        ma_cu = dong["masddv"]
        so = "".join(ch for ch in ma_cu if ch.isdigit())
        tiep_theo = int(so) + 1 if so else 1
        return f"SD{tiep_theo:02d}"

    def tai_du_lieu_su_dung_dich_vu(doi_tuong, tu_khoa=""):
        xoa_du_lieu_bang(doi_tuong.bang_du_lieu)
        tong_tien_tat_ca = 0.0

        with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
            _chuan_hoa_bang_dich_vu(ket_noi)
            cot = _lay_ten_cot_thuc_te(ket_noi)
            doi_tuong._tai_danh_muc_combobox(ket_noi, cot)

            if not doi_tuong.o_ma_sddv.get().strip():
                doi_tuong.o_ma_sddv.insert(0, doi_tuong._sinh_ma_sddv_tu_dong(ket_noi))

            if cot["co_dp"] and cot["co_kh"] and cot["cot_makh_dp"] and cot["ten_kh"]:
                bieu_thuc_khach = (
                    f"COALESCE(kh.{cot['ten_kh']} || ' - P.' || dp.{cot['cot_phong_dp']}, sddv.madat)"
                    if cot["cot_phong_dp"]
                    else f"COALESCE(kh.{cot['ten_kh']}, sddv.madat)"
                )
                sql_goc = f"""
                    SELECT sddv.masddv, sddv.madat,
                           {bieu_thuc_khach} AS thong_tin_khach,
                           COALESCE(dv.{cot['ten_dv']}, sddv.madv) AS tendv,
                           sddv.soluong, sddv.thanhtien,
                           COALESCE(sddv.ngaysudung, '') AS ngaysudung,
                           COALESCE(sddv.ghichu, '') AS ghichu
                    FROM sudungdichvu sddv
                    LEFT JOIN dichvu dv ON sddv.madv = dv.{cot['khoa_dv']}
                    LEFT JOIN datphong dp ON CAST(sddv.madat AS TEXT) = CAST(dp.{cot['khoa_dp']} AS TEXT)
                    LEFT JOIN khachhang kh ON dp.{cot['cot_makh_dp']} = kh.{cot['khoa_kh']}
                """
            else:
                sql_goc = f"""
                    SELECT sddv.masddv, sddv.madat,
                           sddv.madat AS thong_tin_khach,
                           COALESCE(dv.{cot['ten_dv']}, sddv.madv) AS tendv,
                           sddv.soluong, sddv.thanhtien,
                           COALESCE(sddv.ngaysudung, '') AS ngaysudung,
                           COALESCE(sddv.ghichu, '') AS ghichu
                    FROM sudungdichvu sddv
                    LEFT JOIN dichvu dv ON sddv.madv = dv.{cot['khoa_dv']}
                """

            if tu_khoa:
                mau = f"%{tu_khoa}%"
                cac_dong = ket_noi.execute(
                    sql_goc
                    + f"""
                    WHERE sddv.masddv LIKE ? OR sddv.madat LIKE ?
                       OR dv.{cot['ten_dv']} LIKE ? OR sddv.ghichu LIKE ?
                    ORDER BY sddv.masddv DESC
                    """,
                    (mau, mau, mau, mau),
                ).fetchall()
            else:
                cac_dong = ket_noi.execute(
                    sql_goc + " ORDER BY sddv.masddv DESC"
                ).fetchall()

        for chi_so, dong in enumerate(cac_dong):
            nhan_dong = "dong_chan" if chi_so % 2 == 0 else "dong_le"
            thanh_tien = float(dong["thanhtien"] or 0)
            tong_tien_tat_ca += thanh_tien
            doi_tuong.bang_du_lieu.insert(
                "",
                tk.END,
                values=(
                    dong["masddv"],
                    dong["madat"],
                    dong["thong_tin_khach"],
                    dong["tendv"],
                    dong["soluong"],
                    f"{thanh_tien:,.0f} đ",
                    dong["ngaysudung"],
                    dong["ghichu"],
                ),
                tags=(nhan_dong,),
            )

        doi_tuong.nhan_tong_cong.configure(
            text=f"Tổng tiền dịch vụ: {tong_tien_tat_ca:,.0f} VNĐ"
        )

    def xoa_o_nhap(doi_tuong):
        doi_tuong.o_ma_sddv.delete(0, tk.END)
        doi_tuong.o_so_luong.delete(0, tk.END)
        doi_tuong.o_so_luong.insert(0, "1")
        doi_tuong.o_ngay_su_dung.delete(0, tk.END)
        doi_tuong.o_ngay_su_dung.insert(0, datetime.now().strftime("%Y-%m-%d"))
        doi_tuong.o_ghi_chu.delete(0, tk.END)
        for muc in doi_tuong.bang_du_lieu.selection():
            doi_tuong.bang_du_lieu.selection_remove(muc)
        with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
            doi_tuong.o_ma_sddv.insert(0, doi_tuong._sinh_ma_sddv_tu_dong(ket_noi))
        doi_tuong._cap_nhat_thanh_tien_tam_tinh()

    def chon_dong_dich_vu(doi_tuong, _event=None):
        duoc_chon = doi_tuong.bang_du_lieu.selection()
        if not duoc_chon:
            return
        gia_tri = doi_tuong.bang_du_lieu.item(duoc_chon[0], "values")
        doi_tuong.o_ma_sddv.delete(0, tk.END)
        doi_tuong.o_ma_sddv.insert(0, gia_tri[0])

        ma_dat_chon = str(gia_tri[1])
        for nhan, ma in doi_tuong.ban_do_dat_phong.items():
            if ma == ma_dat_chon:
                doi_tuong.hop_dat_phong.set(nhan)
                break

        ten_dv_chon = gia_tri[3]
        for nhan in doi_tuong.ban_do_dich_vu:
            if ten_dv_chon in nhan:
                doi_tuong.hop_dich_vu.set(nhan)
                break

        doi_tuong.o_so_luong.delete(0, tk.END)
        doi_tuong.o_so_luong.insert(0, str(gia_tri[4]))
        doi_tuong.o_ngay_su_dung.delete(0, tk.END)
        doi_tuong.o_ngay_su_dung.insert(0, gia_tri[6])
        doi_tuong.o_ghi_chu.delete(0, tk.END)
        doi_tuong.o_ghi_chu.insert(0, gia_tri[7])
        doi_tuong._cap_nhat_thanh_tien_tam_tinh()

    def _lay_du_lieu_hop_le(doi_tuong):
        ma_sddv = doi_tuong.o_ma_sddv.get().strip().upper()
        nhan_dp = doi_tuong.hop_dat_phong.get().strip()
        nhan_dv = doi_tuong.hop_dich_vu.get().strip()
        ngay_sd = doi_tuong.o_ngay_su_dung.get().strip()
        ghi_chu = doi_tuong.o_ghi_chu.get().strip()

        ma_dat = doi_tuong.ban_do_dat_phong.get(nhan_dp, nhan_dp.split(" - ")[0].strip())
        thong_tin_dv = doi_tuong.ban_do_dich_vu.get(nhan_dv)

        if not ma_sddv or not ma_dat or not thong_tin_dv:
            messagebox.showwarning(
                "Thiếu thông tin",
                "Vui lòng nhập Mã phiếu dịch vụ, chọn Phiếu đặt phòng và Dịch vụ.",
                parent=doi_tuong.cua_so_goc,
            )
            return None

        try:
            so_luong = int(doi_tuong.o_so_luong.get().strip())
            if so_luong <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Số lượng không hợp lệ",
                "Số lượng dịch vụ phải là số nguyên lớn hơn 0.",
                parent=doi_tuong.cua_so_goc,
            )
            return None

        ma_dv, don_gia = thong_tin_dv
        thanh_tien = so_luong * don_gia
        return ma_sddv, ma_dat, ma_dv, so_luong, thanh_tien, ngay_sd, ghi_chu

    def them_su_dung_dich_vu(doi_tuong):
        du_lieu = doi_tuong._lay_du_lieu_hop_le()
        if not du_lieu:
            return
        ma_sddv, ma_dat, ma_dv, so_luong, thanh_tien, ngay_sd, ghi_chu = du_lieu

        try:
            with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
                ket_noi.execute(
                    """
                    INSERT INTO sudungdichvu (masddv, madat, madv, soluong, thanhtien, ngaysudung, ghichu)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (ma_sddv, ma_dat, ma_dv, so_luong, thanh_tien, ngay_sd, ghi_chu),
                )
            messagebox.showinfo(
                "Thành công",
                f"Đã thêm dịch vụ ({ma_sddv}) vào phiếu {ma_dat}!",
                parent=doi_tuong.cua_so_goc,
            )
            doi_tuong.xoa_o_nhap()
            doi_tuong.tai_du_lieu_su_dung_dich_vu()
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Trùng mã",
                f"Mã phiếu dịch vụ '{ma_sddv}' đã tồn tại.",
                parent=doi_tuong.cua_so_goc,
            )

    def sua_su_dung_dich_vu(doi_tuong):
        duoc_chon = doi_tuong.bang_du_lieu.selection()
        if not duoc_chon:
            messagebox.showwarning(
                "Chưa chọn dòng",
                "Vui lòng chọn một dòng sử dụng dịch vụ trong bảng để cập nhật.",
                parent=doi_tuong.cua_so_goc,
            )
            return

        ma_cu = doi_tuong.bang_du_lieu.item(duoc_chon[0], "values")[0]
        du_lieu = doi_tuong._lay_du_lieu_hop_le()
        if not du_lieu:
            return
        ma_moi, ma_dat, ma_dv, so_luong, thanh_tien, ngay_sd, ghi_chu = du_lieu

        try:
            with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
                ket_noi.execute(
                    """
                    UPDATE sudungdichvu
                    SET masddv = ?, madat = ?, madv = ?, soluong = ?, thanhtien = ?, ngaysudung = ?, ghichu = ?
                    WHERE masddv = ?
                    """,
                    (ma_moi, ma_dat, ma_dv, so_luong, thanh_tien, ngay_sd, ghi_chu, ma_cu),
                )
            messagebox.showinfo(
                "Thành công",
                "Cập nhật sử dụng dịch vụ thành công!",
                parent=doi_tuong.cua_so_goc,
            )
            doi_tuong.tai_du_lieu_su_dung_dich_vu()
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Trùng mã",
                "Mã phiếu dịch vụ mới bị trùng với bản ghi khác.",
                parent=doi_tuong.cua_so_goc,
            )

    def xoa_su_dung_dich_vu(doi_tuong):
        duoc_chon = doi_tuong.bang_du_lieu.selection()
        if not duoc_chon:
            messagebox.showwarning(
                "Chưa chọn dòng",
                "Vui lòng chọn một bản ghi dịch vụ cần xóa.",
                parent=doi_tuong.cua_so_goc,
            )
            return

        ma_sddv = doi_tuong.bang_du_lieu.item(duoc_chon[0], "values")[0]
        if messagebox.askyesno(
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa phiếu dịch vụ {ma_sddv}?",
            parent=doi_tuong.cua_so_goc,
        ):
            with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
                ket_noi.execute("DELETE FROM sudungdichvu WHERE masddv = ?", (ma_sddv,))
            messagebox.showinfo(
                "Đã xóa",
                "Xóa sử dụng dịch vụ thành công!",
                parent=doi_tuong.cua_so_goc,
            )
            doi_tuong.xoa_o_nhap()
            doi_tuong.tai_du_lieu_su_dung_dich_vu()

    def tim_kiem_su_dung_dich_vu(doi_tuong):
        doi_tuong.tai_du_lieu_su_dung_dich_vu(doi_tuong.tu_khoa_tim_kiem.get().strip())