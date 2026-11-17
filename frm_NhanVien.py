import sqlite3
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


def _chuan_hoa_bang_nhan_vien(ket_noi):
    """Kiểm tra cấu trúc bảng nhanvien thực tế và trả về tên cột mật khẩu & chức vụ."""
    cac_cot = [
        dong[1] for dong in ket_noi.execute("PRAGMA table_info(nhanvien)").fetchall()
    ]
    if not cac_cot:
        ket_noi.execute(
            """
            CREATE TABLE nhanvien (
                manv TEXT PRIMARY KEY,
                hoten TEXT NOT NULL,
                tendangnhap TEXT UNIQUE NOT NULL,
                matkhau TEXT NOT NULL,
                chucvu TEXT DEFAULT 'Lễ tân'
            )
            """
        )
        return "matkhau", "chucvu"

    # Tìm cột mật khẩu theo các tên phổ biến
    cot_mk = next(
        (
            c
            for c in cac_cot
            if c.lower() in ("matkhau", "mat_khau", "password", "matkhaubam", "mat_khau_bam")
        ),
        None,
    )
    if cot_mk is None:
        ket_noi.execute(
            "ALTER TABLE nhanvien ADD COLUMN matkhau TEXT NOT NULL DEFAULT '123456'"
        )
        cot_mk = "matkhau"

    # Tìm cột chức vụ (hoặc vai trò)
    cot_cv = next(
        (c for c in cac_cot if c.lower() in ("chucvu", "chuc_vu", "vaitro", "role")),
        None,
    )
    if cot_cv is None:
        ket_noi.execute(
            "ALTER TABLE nhanvien ADD COLUMN chucvu TEXT DEFAULT 'Lễ tân'"
        )
        cot_cv = "chucvu"

    return cot_mk, cot_cv


class BieuMauNhanVien:
    def __init__(doi_tuong, ung_dung, khung_cha):
        doi_tuong.ung_dung = ung_dung
        doi_tuong.cua_so_goc = ung_dung.cua_so_goc
        doi_tuong.duong_dan_co_so_du_lieu = getattr(
            ung_dung, "duong_dan_co_so_du_lieu", None
        )
        doi_tuong.khung_cha = khung_cha
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
        dau_trang.pack(fill="x", pady=(0, 14))
        tk.Label(
            dau_trang,
            text="Quản lý nhân viên & Tài khoản",
            font=("Arial", 22, "bold"),
            fg=doi_tuong.dieu_huong_nen,
            bg=doi_tuong.nen_chinh,
        ).pack(anchor="w")
        tk.Label(
            dau_trang,
            text="Thêm, cập nhật thông tin nhân viên, phân quyền chức vụ và cấp tài khoản đăng nhập hệ thống",
            font=("Arial", 10),
            fg=doi_tuong.phu_mau,
            bg=doi_tuong.nen_chinh,
        ).pack(anchor="w", pady=(4, 0))

        # Khung nhập thông tin nhân viên
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

        # Dòng 1: Mã nhân viên, Họ tên, Chức vụ
        tk.Label(khung_nhap, text="Mã nhân viên", **nhan_kieu).grid(
            row=0, column=0, padx=(0, 14), pady=(0, 2), sticky="w"
        )
        doi_tuong.o_ma_nv = ONhapLieuKhachSan(khung_nhap)
        doi_tuong.o_ma_nv.grid(row=1, column=0, padx=(0, 14), pady=(0, 8), sticky="ew")

        tk.Label(khung_nhap, text="Họ và tên nhân viên", **nhan_kieu).grid(
            row=0, column=1, padx=(0, 14), pady=(0, 2), sticky="w"
        )
        doi_tuong.o_ho_ten = ONhapLieuKhachSan(khung_nhap)
        doi_tuong.o_ho_ten.grid(row=1, column=1, padx=(0, 14), pady=(0, 8), sticky="ew")

        tk.Label(khung_nhap, text="Chức vụ", **nhan_kieu).grid(
            row=0, column=2, pady=(0, 2), sticky="w"
        )
        doi_tuong.hop_chuc_vu = OHopChonKhachSan(
            khung_nhap, values=("Quản lý", "Lễ tân", "Kế toán", "Buồng phòng")
        )
        doi_tuong.hop_chuc_vu.set("Lễ tân")
        doi_tuong.hop_chuc_vu.grid(row=1, column=2, pady=(0, 8), sticky="ew")

        # Dòng 2: Tên đăng nhập, Mật khẩu, Tùy chọn hiện mật khẩu
        tk.Label(khung_nhap, text="Tên đăng nhập", **nhan_kieu).grid(
            row=2, column=0, padx=(0, 14), pady=(2, 2), sticky="w"
        )
        doi_tuong.o_ten_dang_nhap = ONhapLieuKhachSan(khung_nhap)
        doi_tuong.o_ten_dang_nhap.grid(
            row=3, column=0, padx=(0, 14), pady=(0, 4), sticky="ew"
        )

        tk.Label(khung_nhap, text="Mật khẩu", **nhan_kieu).grid(
            row=2, column=1, padx=(0, 14), pady=(2, 2), sticky="w"
        )
        doi_tuong.o_mat_khau = ONhapLieuKhachSan(khung_nhap, show="•")
        doi_tuong.o_mat_khau.grid(
            row=3, column=1, padx=(0, 14), pady=(0, 4), sticky="ew"
        )

        doi_tuong.hien_mat_khau = tk.BooleanVar(value=False)
        tk.Checkbutton(
            khung_nhap,
            text="Hiển thị mật khẩu",
            variable=doi_tuong.hien_mat_khau,
            command=lambda: doi_tuong.o_mat_khau.configure(
                show="" if doi_tuong.hien_mat_khau.get() else "•"
            ),
            bg=doi_tuong.the_nen,
            fg=doi_tuong.van_ban_mau,
            activebackground=doi_tuong.the_nen,
            selectcolor=doi_tuong.the_nen,
            font=("Arial", 9),
            cursor="hand2",
        ).grid(row=3, column=2, sticky="w", pady=(0, 4))

        for cot in range(3):
            khung_nhap.grid_columnconfigure(cot, weight=1)

        # Thanh nút chức năng CRUD
        cac_thao_tac = tk.Frame(noi_dung, bg=doi_tuong.nen_chinh)
        cac_thao_tac.pack(fill="x", pady=12)
        tao_nut_khach_san(
            cac_thao_tac,
            "Thêm nhân viên",
            doi_tuong.them_nhan_vien,
            doi_tuong.dieu_huong_nen,
        ).pack(side="left", padx=(0, 8))
        tao_nut_khach_san(
            cac_thao_tac,
            "Cập nhật thông tin",
            doi_tuong.sua_nhan_vien,
            doi_tuong.nhan_manh_mau,
        ).pack(side="left", padx=4)
        tao_nut_khach_san(
            cac_thao_tac,
            "Xóa nhân viên",
            doi_tuong.xoa_nhan_vien,
            "#B91C1C",
        ).pack(side="left", padx=4)
        tao_nut_khach_san(
            cac_thao_tac,
            "Xóa trống ô nhập",
            doi_tuong.xoa_o_nhap,
            "#52615D",
        ).pack(side="left", padx=4)

        # Khung tìm kiếm & bảng danh sách nhân viên
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
        o_tim.bind("<Return>", lambda _: doi_tuong.tim_kiem_nhan_vien())

        tao_nut_khach_san(
            khung_tim,
            "Tìm kiếm",
            doi_tuong.tim_kiem_nhan_vien,
            doi_tuong.dieu_huong_nen,
            padx=12,
        ).pack(side="left", padx=(8, 4))
        tao_nut_khach_san(
            khung_tim,
            "Làm mới",
            lambda: (
                doi_tuong.tu_khoa_tim_kiem.set(""),
                doi_tuong.tai_du_lieu_nhan_vien(),
            ),
            "#475569",
            padx=12,
        ).pack(side="left", padx=4)

        doi_tuong.bang_du_lieu = tao_bang_du_lieu(
            the_bang,
            ("manv", "hoten", "tendangnhap", "chucvu", "matkhau"),
            ("Mã NV", "Họ và tên", "Tên đăng nhập", "Chức vụ", "Mật khẩu"),
            (110, 240, 180, 150, 160),
            ("center", "w", "w", "center", "center"),
            mau_nen=doi_tuong.the_nen,
        )
        doi_tuong.bang_du_lieu.bind("<<TreeviewSelect>>", doi_tuong.chon_nhan_vien)

        doi_tuong.tai_du_lieu_nhan_vien()
        return noi_dung

    def tai_du_lieu_nhan_vien(doi_tuong, tu_khoa=""):
        xoa_du_lieu_bang(doi_tuong.bang_du_lieu)
        with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
            cot_mk, cot_cv = _chuan_hoa_bang_nhan_vien(ket_noi)
            if tu_khoa:
                mau = f"%{tu_khoa}%"
                cac_dong = ket_noi.execute(
                    f"""
                    SELECT manv, hoten, tendangnhap, {cot_cv} AS chucvu, {cot_mk} AS matkhau
                    FROM nhanvien
                    WHERE manv LIKE ? OR hoten LIKE ? OR tendangnhap LIKE ? OR {cot_cv} LIKE ?
                    ORDER BY manv
                    """,
                    (mau, mau, mau, mau),
                ).fetchall()
            else:
                cac_dong = ket_noi.execute(
                    f"""
                    SELECT manv, hoten, tendangnhap, {cot_cv} AS chucvu, {cot_mk} AS matkhau
                    FROM nhanvien
                    ORDER BY manv
                    """
                ).fetchall()

        for chi_so, dong in enumerate(cac_dong):
            nhan_dong = "dong_chan" if chi_so % 2 == 0 else "dong_le"
            doi_tuong.bang_du_lieu.insert(
                "",
                tk.END,
                values=(
                    dong["manv"],
                    dong["hoten"],
                    dong["tendangnhap"],
                    dong["chucvu"] or "",
                    dong["matkhau"],
                ),
                tags=(nhan_dong,),
            )

    def xoa_o_nhap(doi_tuong):
        doi_tuong.o_ma_nv.delete(0, tk.END)
        doi_tuong.o_ho_ten.delete(0, tk.END)
        doi_tuong.o_ten_dang_nhap.delete(0, tk.END)
        doi_tuong.o_mat_khau.delete(0, tk.END)
        doi_tuong.hop_chuc_vu.set("Lễ tân")
        for muc in doi_tuong.bang_du_lieu.selection():
            doi_tuong.bang_du_lieu.selection_remove(muc)

    def chon_nhan_vien(doi_tuong, _event=None):
        duoc_chon = doi_tuong.bang_du_lieu.selection()
        if not duoc_chon:
            return
        gia_tri = doi_tuong.bang_du_lieu.item(duoc_chon[0], "values")
        doi_tuong.o_ma_nv.delete(0, tk.END)
        doi_tuong.o_ma_nv.insert(0, gia_tri[0])
        doi_tuong.o_ho_ten.delete(0, tk.END)
        doi_tuong.o_ho_ten.insert(0, gia_tri[1])
        doi_tuong.o_ten_dang_nhap.delete(0, tk.END)
        doi_tuong.o_ten_dang_nhap.insert(0, gia_tri[2])
        doi_tuong.hop_chuc_vu.set(gia_tri[3] or "Lễ tân")
        doi_tuong.o_mat_khau.delete(0, tk.END)
        doi_tuong.o_mat_khau.insert(0, gia_tri[4])

    def them_nhan_vien(doi_tuong):
        ma_nv = doi_tuong.o_ma_nv.get().strip().upper()
        ho_ten = doi_tuong.o_ho_ten.get().strip()
        ten_dang_nhap = doi_tuong.o_ten_dang_nhap.get().strip()
        mat_khau = doi_tuong.o_mat_khau.get().strip()
        chuc_vu = doi_tuong.hop_chuc_vu.get().strip()

        if not ma_nv or not ho_ten or not ten_dang_nhap or not mat_khau:
            messagebox.showwarning(
                "Thiếu thông tin",
                "Vui lòng nhập đầy đủ Mã nhân viên, Họ tên, Tên đăng nhập và Mật khẩu.",
                parent=doi_tuong.cua_so_goc,
            )
            return

        if len(mat_khau) < 4:
            messagebox.showwarning(
                "Mật khẩu quá ngắn",
                "Mật khẩu phải có ít nhất 4 ký tự.",
                parent=doi_tuong.cua_so_goc,
            )
            return

        try:
            with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
                cot_mk, cot_cv = _chuan_hoa_bang_nhan_vien(ket_noi)
                ket_noi.execute(
                    f"""
                    INSERT INTO nhanvien (manv, hoten, tendangnhap, {cot_mk}, {cot_cv})
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (ma_nv, ho_ten, ten_dang_nhap, mat_khau, chuc_vu),
                )
            messagebox.showinfo(
                "Thành công",
                f"Đã thêm nhân viên {ho_ten} ({ma_nv}) thành công!",
                parent=doi_tuong.cua_so_goc,
            )
            doi_tuong.xoa_o_nhap()
            doi_tuong.tai_du_lieu_nhan_vien()
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Trùng dữ liệu",
                "Mã nhân viên hoặc Tên đăng nhập đã tồn tại trong hệ thống.",
                parent=doi_tuong.cua_so_goc,
            )

    def sua_nhan_vien(doi_tuong):
        duoc_chon = doi_tuong.bang_du_lieu.selection()
        if not duoc_chon:
            messagebox.showwarning(
                "Chưa chọn nhân viên",
                "Vui lòng chọn một nhân viên trong bảng danh sách để cập nhật.",
                parent=doi_tuong.cua_so_goc,
            )
            return

        ma_nv_cu = doi_tuong.bang_du_lieu.item(duoc_chon[0], "values")[0]
        ma_nv_moi = doi_tuong.o_ma_nv.get().strip().upper()
        ho_ten = doi_tuong.o_ho_ten.get().strip()
        ten_dang_nhap = doi_tuong.o_ten_dang_nhap.get().strip()
        mat_khau = doi_tuong.o_mat_khau.get().strip()
        chuc_vu = doi_tuong.hop_chuc_vu.get().strip()

        if not ma_nv_moi or not ho_ten or not ten_dang_nhap or not mat_khau:
            messagebox.showwarning(
                "Thiếu thông tin",
                "Vui lòng nhập đầy đủ thông tin nhân viên trước khi lưu.",
                parent=doi_tuong.cua_so_goc,
            )
            return

        if len(mat_khau) < 4:
            messagebox.showwarning(
                "Mật khẩu quá ngắn",
                "Mật khẩu phải có ít nhất 4 ký tự.",
                parent=doi_tuong.cua_so_goc,
            )
            return

        try:
            with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
                cot_mk, cot_cv = _chuan_hoa_bang_nhan_vien(ket_noi)
                ket_noi.execute(
                    f"""
                    UPDATE nhanvien
                    SET manv = ?, hoten = ?, tendangnhap = ?, {cot_mk} = ?, {cot_cv} = ?
                    WHERE manv = ?
                    """,
                    (ma_nv_moi, ho_ten, ten_dang_nhap, mat_khau, chuc_vu, ma_nv_cu),
                )
            messagebox.showinfo(
                "Thành công",
                "Cập nhật thông tin nhân viên thành công!",
                parent=doi_tuong.cua_so_goc,
            )
            doi_tuong.tai_du_lieu_nhan_vien()
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Trùng dữ liệu",
                "Mã nhân viên hoặc Tên đăng nhập bị trùng với tài khoản khác.",
                parent=doi_tuong.cua_so_goc,
            )

    def xoa_nhan_vien(doi_tuong):
        duoc_chon = doi_tuong.bang_du_lieu.selection()
        if not duoc_chon:
            messagebox.showwarning(
                "Chưa chọn nhân viên",
                "Vui lòng chọn một nhân viên cần xóa.",
                parent=doi_tuong.cua_so_goc,
            )
            return

        gia_tri = doi_tuong.bang_du_lieu.item(duoc_chon[0], "values")
        ma_nv = gia_tri[0]
        ho_ten = gia_tri[1]
        ten_dang_nhap = gia_tri[2]

        nv_hien_tai = getattr(doi_tuong.ung_dung, "nhan_vien_hien_tai", None)
        if nv_hien_tai and nv_hien_tai.get("tendangnhap") == ten_dang_nhap:
            messagebox.showwarning(
                "Không thể xóa",
                "Bạn không thể xóa tài khoản nhân viên đang đăng nhập phiên hiện tại!",
                parent=doi_tuong.cua_so_goc,
            )
            return

        if messagebox.askyesno(
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa nhân viên {ho_ten} ({ma_nv})?",
            parent=doi_tuong.cua_so_goc,
        ):
            with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
                so_luong = ket_noi.execute("SELECT COUNT(*) FROM nhanvien").fetchone()[0]
                if so_luong <= 1:
                    messagebox.showwarning(
                        "Không thể xóa",
                        "Hệ thống phải duy trì ít nhất 1 tài khoản nhân viên.",
                        parent=doi_tuong.cua_so_goc,
                    )
                    return
                ket_noi.execute("DELETE FROM nhanvien WHERE manv = ?", (ma_nv,))
            messagebox.showinfo(
                "Đã xóa",
                "Xóa nhân viên thành công!",
                parent=doi_tuong.cua_so_goc,
            )
            doi_tuong.xoa_o_nhap()
            doi_tuong.tai_du_lieu_nhan_vien()

    def tim_kiem_nhan_vien(doi_tuong):
        doi_tuong.tai_du_lieu_nhan_vien(doi_tuong.tu_khoa_tim_kiem.get().strip())