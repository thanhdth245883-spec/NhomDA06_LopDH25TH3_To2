from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from employee_auth import xac_thuc_dang_nhap
from ui_components import (
    BANG_MAU_KHACH_SAN,
    ONhapLieuKhachSan,
    cau_hinh_giao_dien_ttk,
    tao_nut_khach_san,
)


class BieuMauDangNhap:
    def __init__(
        doi_tuong,
        cua_so_goc,
        duong_dan_co_so_du_lieu=None,
        khi_dang_nhap_thanh_cong=None,
    ):
        doi_tuong.cua_so_goc = cua_so_goc
        doi_tuong.duong_dan_co_so_du_lieu = (
            Path(duong_dan_co_so_du_lieu)
            if duong_dan_co_so_du_lieu
            else Path(__file__).with_name("QLKS.db")
        )
        doi_tuong.khi_dang_nhap_thanh_cong = khi_dang_nhap_thanh_cong
        doi_tuong.nhan_vien_hien_tai = None

        for ten, gia_tri in BANG_MAU_KHACH_SAN.items():
            setattr(doi_tuong, ten, gia_tri)

    def tao_giao_dien(doi_tuong):
        doi_tuong.cua_so_goc.title("Đăng nhập hệ thống - THANHVY Hotel")
        doi_tuong.cua_so_goc.configure(bg=doi_tuong.nen_chinh)
        doi_tuong._can_giua_cua_so(460, 520)
        doi_tuong.cua_so_goc.resizable(False, False)

        # Khung viền ngoài đồng bộ phong cách BieuMauTrangChu
        khung_ngoai = tk.Frame(
            doi_tuong.cua_so_goc,
            bg=doi_tuong.dieu_huong_nen,
            padx=3,
            pady=3,
            highlightthickness=1,
            highlightbackground=doi_tuong.nhan_manh_mau,
        )
        khung_ngoai.pack(fill="both", expand=True, padx=18, pady=18)

        noi_dung = tk.Frame(khung_ngoai, bg=doi_tuong.the_nen, padx=32, pady=28)
        noi_dung.pack(fill="both", expand=True)

        # Phần tiêu đề thương hiệu
        tk.Label(
            noi_dung,
            text="T H A N H V Y  H O T E L",
            bg=doi_tuong.the_nen,
            fg=doi_tuong.nhan_manh_mau,
            font=("Arial", 10, "bold"),
        ).pack(pady=(4, 6))

        tk.Label(
            noi_dung,
            text="ĐĂNG NHẬP HỆ THỐNG",
            bg=doi_tuong.the_nen,
            fg=doi_tuong.dieu_huong_nen,
            font=("Arial", 19, "bold"),
        ).pack()

        tk.Label(
            noi_dung,
            text="Phần mềm Quản lý Khách sạn • SQLite3",
            bg=doi_tuong.the_nen,
            fg=doi_tuong.phu_mau,
            font=("Arial", 9),
        ).pack(pady=(4, 14))

        tk.Frame(noi_dung, bg=doi_tuong.nhan_manh_mau, height=2).pack(
            fill="x", padx=30, pady=(0, 18)
        )

        # Khung nhập tài khoản & mật khẩu
        khung_nhap = tk.Frame(noi_dung, bg=doi_tuong.the_nen)
        khung_nhap.pack(fill="x")

        nhan_kieu = {
            "bg": doi_tuong.the_nen,
            "fg": doi_tuong.van_ban_mau,
            "font": ("Arial", 9, "bold"),
        }

        tk.Label(khung_nhap, text="Tên đăng nhập", **nhan_kieu).pack(
            anchor="w", pady=(0, 4)
        )
        doi_tuong.o_nhap_tai_khoan = ONhapLieuKhachSan(khung_nhap)
        doi_tuong.o_nhap_tai_khoan.pack(fill="x", pady=(0, 14))

        tk.Label(khung_nhap, text="Mật khẩu", **nhan_kieu).pack(
            anchor="w", pady=(0, 4)
        )
        doi_tuong.o_nhap_mat_khau = ONhapLieuKhachSan(khung_nhap, show="•")
        doi_tuong.o_nhap_mat_khau.pack(fill="x", pady=(0, 8))

        # Tùy chọn hiện/ẩn mật khẩu
        doi_tuong.hien_mat_khau_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            khung_nhap,
            text="Hiển thị mật khẩu",
            variable=doi_tuong.hien_mat_khau_var,
            command=doi_tuong._chuyen_hien_mat_khau,
            bg=doi_tuong.the_nen,
            fg=doi_tuong.phu_mau,
            activebackground=doi_tuong.the_nen,
            selectcolor=doi_tuong.the_nen,
            font=("Arial", 9),
            cursor="hand2",
        ).pack(anchor="w", pady=(0, 14))

        # Nhãn thông báo trạng thái nhanh ngay trên form
        doi_tuong.nhan_thong_bao = tk.Label(
            noi_dung,
            text="",
            bg=doi_tuong.the_nen,
            fg="#B91C1C",
            font=("Arial", 9, "italic"),
            wraplength=340,
            justify="center",
        )
        doi_tuong.nhan_thong_bao.pack(pady=(0, 10))

        # Thanh nút bấm
        khung_nut = tk.Frame(noi_dung, bg=doi_tuong.the_nen)
        khung_nut.pack(pady=(4, 12))

        tao_nut_khach_san(
            khung_nut,
            "ĐĂNG NHẬP",
            doi_tuong.xu_ly_dang_nhap,
            doi_tuong.dieu_huong_nen,
            padx=22,
        ).pack(side="left", padx=6)

        tao_nut_khach_san(
            khung_nut,
            "THOÁT",
            doi_tuong.cua_so_goc.destroy,
            "#64748B",
            padx=18,
        ).pack(side="left", padx=6)

        # Gợi ý tài khoản mẫu phục vụ kiểm thử đồ án
        tk.Label(
            noi_dung,
            text="Tài khoản mẫu: admin / 123456 •  nhanvien1 / Nhanvien123!",
            bg=doi_tuong.the_nen,
            fg=doi_tuong.phu_mau,
            font=("Arial", 8, "italic"),
        ).pack(side="bottom", pady=(6, 0))

        # Phím tắt Enter để đăng nhập nhanh
        doi_tuong.o_nhap_tai_khoan.bind(
            "<Return>", lambda _: doi_tuong.o_nhap_mat_khau.focus_set()
        )
        doi_tuong.o_nhap_mat_khau.bind(
            "<Return>", lambda _: doi_tuong.xu_ly_dang_nhap()
        )
        doi_tuong.o_nhap_tai_khoan.focus_set()
        return khung_ngoai

    def _can_giua_cua_so(doi_tuong, chieu_rong, chieu_cao):
        doi_tuong.cua_so_goc.update_idletasks()
        rong_man_hinh = doi_tuong.cua_so_goc.winfo_screenwidth()
        cao_man_hinh = doi_tuong.cua_so_goc.winfo_screenheight()
        x = (rong_man_hinh - chieu_rong) // 2
        y = (cao_man_hinh - chieu_cao) // 2
        doi_tuong.cua_so_goc.geometry(f"{chieu_rong}x{chieu_cao}+{x}+{y}")

    def _chuyen_hien_mat_khau(doi_tuong):
        ky_tu_che = "" if doi_tuong.hien_mat_khau_var.get() else "•"
        doi_tuong.o_nhap_mat_khau.configure(show=ky_tu_che)

    def xu_ly_dang_nhap(doi_tuong):
        tai_khoan = doi_tuong.o_nhap_tai_khoan.get().strip()
        mat_khau = doi_tuong.o_nhap_mat_khau.get()

        if not tai_khoan or not mat_khau:
            doi_tuong.nhan_thong_bao.config(
                text="Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu."
            )
            if not tai_khoan:
                doi_tuong.o_nhap_tai_khoan.focus_set()
            else:
                doi_tuong.o_nhap_mat_khau.focus_set()
            return

        if not doi_tuong.duong_dan_co_so_du_lieu.exists():
            messagebox.showerror(
                "Thiếu cơ sở dữ liệu",
                f"Không tìm thấy tệp cơ sở dữ liệu tại:\n{doi_tuong.duong_dan_co_so_du_lieu}",
                parent=doi_tuong.cua_so_goc,
            )
            return

        nhan_vien = xac_thuc_dang_nhap(
            tai_khoan,
            mat_khau,
            doi_tuong.duong_dan_co_so_du_lieu,
        )

        if nhan_vien is None:
            doi_tuong.nhan_thong_bao.config(
                text="Tên đăng nhập hoặc mật khẩu không chính xác!"
            )
            doi_tuong.o_nhap_mat_khau.delete(0, tk.END)
            doi_tuong.o_nhap_mat_khau.focus_set()
            return

        doi_tuong.nhan_thong_bao.config(text="")
        doi_tuong.nhan_vien_hien_tai = nhan_vien

        # Hủy form đăng nhập và mở cửa sổ chính
        for widget in doi_tuong.cua_so_goc.winfo_children():
            widget.destroy()

        if callable(doi_tuong.khi_dang_nhap_thanh_cong):
            doi_tuong.khi_dang_nhap_thanh_cong(nhan_vien)


def mo_cua_so_chinh_mac_dinh(cua_so_goc, nhan_vien, duong_dan_db):
    """Hàm mở giao diện chính khi chạy độc lập frm_dang_nhap.py."""
    from frm_TrangChu import BieuMauTrangChu

    cua_so_goc.resizable(True, True)
    cua_so_goc.title(
        f"THANHVY Hotel - Xin chào {nhan_vien['hoten']} ({nhan_vien['chucvu']})"
    )
    cua_so_goc.geometry("1120x720")

    class UngDungChinh:
        def __init__(self, root, nv):
            self.cua_so_goc = root
            self.duong_dan_co_so_du_lieu = duong_dan_db
            self.duong_dan_db = duong_dan_db
            self.nhan_vien_hien_tai = nv
            for ten, gia_tri in BANG_MAU_KHACH_SAN.items():
                setattr(self, ten, gia_tri)

            # Thanh điều hướng trên cùng hiển thị nhân viên đang đăng nhập
            thanh_tren = tk.Frame(root, bg=self.dieu_huong_nen, padx=18, pady=10)
            thanh_tren.pack(fill="x")

            tk.Label(
                thanh_tren,
                text="THANHVY HOTEL",
                bg=self.dieu_huong_nen,
                fg=self.nhan_manh_mau,
                font=("Arial", 12, "bold"),
            ).pack(side="left")

            tk.Label(
                thanh_tren,
                text=f"Nhân viên: {nv['hoten']} ({nv['manv']})  •  Chức vụ: {nv['chucvu']}",
                bg=self.dieu_huong_nen,
                fg="#FFFFFF",
                font=("Arial", 10),
            ).pack(side="right")

            self.vung_noi_dung = tk.Frame(root, bg=self.nen_chinh)
            self.vung_noi_dung.pack(fill="both", expand=True)

        def hien_thi_trang(self, ten_trang):
            for widget in self.vung_noi_dung.winfo_children():
                widget.destroy()

            if ten_trang == "customers":
                from frm_KhachHang import BieuMauKhachHang

                BieuMauKhachHang(self, self.vung_noi_dung).tao_giao_dien()
            else:
                BieuMauTrangChu(self, self.vung_noi_dung).tao_giao_dien()

    app = UngDungChinh(cua_so_goc, nhan_vien)
    app.hien_thi_trang("home")


if __name__ == "__main__":
    duong_dan_db = Path(__file__).with_name("QLKS.db")
    cua_so = tk.Tk()
    cau_hinh_giao_dien_ttk(cua_so)

    bieu_mau_dn = BieuMauDangNhap(
        cua_so,
        duong_dan_co_so_du_lieu=duong_dan_db,
        khi_dang_nhap_thanh_cong=lambda nv: mo_cua_so_chinh_mac_dinh(
            cua_so, nv, duong_dan_db
        ),
    )
    bieu_mau_dn.tao_giao_dien()
    cua_so.mainloop()