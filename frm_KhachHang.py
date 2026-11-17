import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from db_connection import mo_ket_noi_co_so_du_lieu
from ui_components import (
    BANG_MAU_KHACH_SAN,
    ONhapLieuKhachSan,
    cau_hinh_giao_dien_ttk,
    tao_bang_du_lieu,
    tao_nut_khach_san,
    xoa_du_lieu_bang,
)


def _cac_truong_khach_hang_con_thieu(thong_tin):
    ten_truong = ("Mã khách hàng", "Họ và tên", "CCCD/CMND", "Số điện thoại", "Giới tính")
    return [
        ten
        for ten, gia_tri in zip(ten_truong, thong_tin)
        if not gia_tri.strip()
    ]


def _cac_truong_so_khong_hop_le(cccd, so_dien_thoai):
    cac_truong_khong_hop_le = []
    if not cccd.isdigit():
        cac_truong_khong_hop_le.append("CCCD/CMND")
    if not so_dien_thoai.isdigit():
        cac_truong_khong_hop_le.append("Số điện thoại")
    return cac_truong_khong_hop_le


class BieuMauKhachHang:
    def __init__(doi_tuong, ung_dung, khung_cha):
        doi_tuong.cua_so_goc = ung_dung.cua_so_goc
        doi_tuong.duong_dan_co_so_du_lieu = getattr(
            ung_dung, "duong_dan_co_so_du_lieu", None
        )
        doi_tuong.khung_cha = khung_cha
        doi_tuong.ma_khach_hang_dang_sua = None
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
        dau_trang.pack(fill="x", pady=(0, 16))
        tk.Label(
            dau_trang,
            text="Quản lý khách hàng",
            font=("Arial", 22, "bold"),
            fg=doi_tuong.dieu_huong_nen,
            bg=doi_tuong.nen_chinh,
        ).pack(anchor="w")
        tk.Label(
            dau_trang,
            text="Theo dõi thông tin, CCCD/CMND và hồ sơ khách lưu trú tại Aurelia Hotel",
            font=("Arial", 10),
            fg=doi_tuong.phu_mau,
            bg=doi_tuong.nen_chinh,
        ).pack(anchor="w", pady=(4, 0))

        # Khung nhập thông tin khách hàng
        khung_thong_tin = tk.Frame(
            noi_dung,
            bg=doi_tuong.the_nen,
            padx=20,
            pady=16,
            highlightthickness=1,
            highlightbackground=BANG_MAU_KHACH_SAN["vien_the"],
        )
        khung_thong_tin.pack(fill="x")
        tk.Label(
            khung_thong_tin,
            text="THÔNG TIN KHÁCH HÀNG",
            font=("Arial", 10, "bold"),
            fg=doi_tuong.nhan_manh_mau,
            bg=doi_tuong.the_nen,
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

        nhan_kieu = {
            "bg": doi_tuong.the_nen,
            "fg": doi_tuong.phu_mau,
            "font": ("Arial", 9, "bold"),
        }
        cac_truong = (
            ("Mã khách hàng", "o_nhap_ma_khach_hang", 1, 0),
            ("CCCD / CMND", "o_nhap_cccd", 1, 2),
            ("Họ và tên", "o_nhap_ho_ten", 3, 0),
            ("Số điện thoại", "o_nhap_so_dien_thoai", 3, 2),
        )
        for nhan, thuoc_tinh, dong, cot in cac_truong:
            tk.Label(khung_thong_tin, text=nhan, **nhan_kieu).grid(
                row=dong, column=cot, padx=(0, 10), pady=(4, 2), sticky="w"
            )
            o_nhap = ONhapLieuKhachSan(khung_thong_tin)
            setattr(doi_tuong, thuoc_tinh, o_nhap)
            o_nhap.grid(
                row=dong + 1,
                column=cot,
                columnspan=2,
                padx=(0, 18),
                pady=(0, 8),
                sticky="ew",
            )

        tk.Label(khung_thong_tin, text="Giới tính", **nhan_kieu).grid(
            row=5, column=0, padx=(0, 10), pady=(3, 0), sticky="w"
        )
        doi_tuong.gioi_tinh_nhap = tk.StringVar(value="Nam")
        khung_gioi_tinh = tk.Frame(khung_thong_tin, bg=doi_tuong.the_nen)
        khung_gioi_tinh.grid(row=5, column=1, columnspan=3, sticky="w")
        for gia_tri in ("Nam", "Nữ"):
            tk.Radiobutton(
                khung_gioi_tinh,
                text=gia_tri,
                variable=doi_tuong.gioi_tinh_nhap,
                value=gia_tri,
                bg=doi_tuong.the_nen,
                fg=doi_tuong.van_ban_mau,
                activebackground=doi_tuong.the_nen,
                selectcolor=BANG_MAU_KHACH_SAN["chon_dong"],
                font=("Arial", 9, "bold"),
                cursor="hand2",
            ).pack(side="left", padx=(0, 18))

        khung_thong_tin.grid_columnconfigure(1, weight=1)
        khung_thong_tin.grid_columnconfigure(3, weight=1)

        # Thanh nút thao tác CRUD
        cac_thao_tac = tk.Frame(noi_dung, bg=doi_tuong.nen_chinh)
        cac_thao_tac.pack(fill="x", pady=14)
        tao_nut_khach_san(
            cac_thao_tac,
            "Thêm khách",
            doi_tuong.them_khach_hang,
            doi_tuong.dieu_huong_nen,
        ).pack(side="left", padx=(0, 8))
        tao_nut_khach_san(
            cac_thao_tac,
            "Lưu thay đổi",
            doi_tuong.luu_khach_hang,
            doi_tuong.nhan_manh_mau,
        ).pack(side="left", padx=4)
        tao_nut_khach_san(
            cac_thao_tac,
            "Chỉnh sửa",
            doi_tuong.chinh_sua_khach_hang,
            "#2563EB",
        ).pack(side="left", padx=4)
        tao_nut_khach_san(
            cac_thao_tac,
            "Hủy nhập",
            doi_tuong.xoa_trang_o_nhap,
            "#475569",
        ).pack(side="left", padx=4)
        tao_nut_khach_san(
            cac_thao_tac,
            "Xóa khách",
            doi_tuong.xoa_khach_hang,
            "#B91C1C",
        ).pack(side="left", padx=4)

        # Khung tìm kiếm & bảng danh sách khách hàng
        the_bang_du_lieu = tk.Frame(
            noi_dung,
            bg=doi_tuong.the_nen,
            padx=16,
            pady=13,
            highlightthickness=1,
            highlightbackground=BANG_MAU_KHACH_SAN["vien_the"],
        )
        the_bang_du_lieu.pack(fill="both", expand=True)

        cac_dieu_khien_tim_kiem = tk.Frame(the_bang_du_lieu, bg=doi_tuong.the_nen)
        cac_dieu_khien_tim_kiem.pack(fill="x", pady=(0, 10))
        doi_tuong.tu_khoa_tim_kiem = tk.StringVar()
        doi_tuong.o_nhap_tim_kiem = ONhapLieuKhachSan(
            cac_dieu_khien_tim_kiem,
            textvariable=doi_tuong.tu_khoa_tim_kiem,
        )
        doi_tuong.o_nhap_tim_kiem.pack(side="left", fill="x", expand=True)
        doi_tuong.o_nhap_tim_kiem.bind(
            "<Return>", lambda _: doi_tuong.tai_du_lieu_khach_hang()
        )

        tao_nut_khach_san(
            cac_dieu_khien_tim_kiem,
            "Tìm khách",
            doi_tuong.tai_du_lieu_khach_hang,
            doi_tuong.dieu_huong_nen,
            padx=12,
        ).pack(side="left", padx=(8, 4))
        tao_nut_khach_san(
            cac_dieu_khien_tim_kiem,
            "Xóa tìm kiếm",
            lambda: (
                doi_tuong.tu_khoa_tim_kiem.set(""),
                doi_tuong.tai_du_lieu_khach_hang(),
            ),
            "#475569",
            padx=12,
        ).pack(side="left", padx=4)

        doi_tuong.bang_du_lieu = tao_bang_du_lieu(
            the_bang_du_lieu,
            ("makh", "hoten", "cccd", "sodt", "gioitinh"),
            ("Mã KH", "Họ và tên", "CCCD/CMND", "Số điện thoại", "Giới tính"),
            (110, 250, 180, 180, 110),
            ("center", "w", "center", "center", "center"),
            mau_nen=doi_tuong.the_nen,
        )

        def khi_chon_khach_hang(event=None):
            duoc_chon = doi_tuong.bang_du_lieu.selection()
            if not duoc_chon:
                return
            gia_tri = doi_tuong.bang_du_lieu.item(duoc_chon[0], "values")
            doi_tuong.xoa_trang_o_nhap()
            doi_tuong.ma_khach_hang_dang_sua = gia_tri[0]
            doi_tuong.o_nhap_ma_khach_hang.insert(0, gia_tri[0])
            doi_tuong.o_nhap_ma_khach_hang.configure(state="readonly")
            doi_tuong.o_nhap_ho_ten.insert(0, gia_tri[1])
            doi_tuong.o_nhap_cccd.insert(0, gia_tri[2])
            doi_tuong.o_nhap_so_dien_thoai.insert(0, gia_tri[3] or "")
            doi_tuong.gioi_tinh_nhap.set(
                gia_tri[4] if gia_tri[4] in ("Nam", "Nữ") else "Nam"
            )

        doi_tuong.bang_du_lieu.bind("<<TreeviewSelect>>", khi_chon_khach_hang)
        doi_tuong.tai_du_lieu_khach_hang()
        return noi_dung

    def xoa_trang_o_nhap(doi_tuong):
        doi_tuong.o_nhap_ma_khach_hang.configure(state="normal")
        doi_tuong.o_nhap_ma_khach_hang.delete(0, tk.END)
        doi_tuong.o_nhap_ho_ten.delete(0, tk.END)
        doi_tuong.o_nhap_cccd.delete(0, tk.END)
        doi_tuong.o_nhap_so_dien_thoai.delete(0, tk.END)
        doi_tuong.gioi_tinh_nhap.set("Nam")
        doi_tuong.ma_khach_hang_dang_sua = None

    def tai_du_lieu_khach_hang(doi_tuong):
        xoa_du_lieu_bang(doi_tuong.bang_du_lieu)
        tu_khoa = doi_tuong.tu_khoa_tim_kiem.get().strip()
        with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
            if tu_khoa:
                tham_so_tim_kiem = f"%{tu_khoa}%"
                cac_dong = ket_noi.execute(
                    """
                    SELECT makh, hoten, cccd, sodt, gioitinh
                    FROM khachhang
                    WHERE makh LIKE ? OR hoten LIKE ? OR cccd LIKE ? OR sodt LIKE ?
                    ORDER BY makh
                    """,
                    (
                        tham_so_tim_kiem,
                        tham_so_tim_kiem,
                        tham_so_tim_kiem,
                        tham_so_tim_kiem,
                    ),
                ).fetchall()
            else:
                cac_dong = ket_noi.execute(
                    "SELECT makh, hoten, cccd, sodt, gioitinh FROM khachhang ORDER BY makh"
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
                ),
                tags=(nhan_dong,),
            )

    def them_khach_hang(doi_tuong):
        if doi_tuong.ma_khach_hang_dang_sua is not None:
            messagebox.showwarning(
                "Đang ở chế độ chỉnh sửa",
                "Bạn đang chọn một khách hàng có sẵn. Vui lòng nhấn 'Hủy nhập' trước khi thêm khách mới.",
                parent=doi_tuong.cua_so_goc,
            )
            return

        ma_khach_hang = doi_tuong.o_nhap_ma_khach_hang.get().strip().upper()
        ho_ten = doi_tuong.o_nhap_ho_ten.get().strip()
        cccd = doi_tuong.o_nhap_cccd.get().strip()
        so_dien_thoai = doi_tuong.o_nhap_so_dien_thoai.get().strip()
        gioi_tinh = doi_tuong.gioi_tinh_nhap.get()

        cac_truong_con_thieu = _cac_truong_khach_hang_con_thieu(
            (ma_khach_hang, ho_ten, cccd, so_dien_thoai, gioi_tinh)
        )
        if cac_truong_con_thieu:
            messagebox.showwarning(
                "Thiếu thông tin",
                "Vui lòng nhập đầy đủ thông tin khách hàng. Còn thiếu: "
                + ", ".join(cac_truong_con_thieu)
                + ".",
                parent=doi_tuong.cua_so_goc,
            )
            return

        cac_truong_so_khong_hop_le = _cac_truong_so_khong_hop_le(
            cccd, so_dien_thoai
        )
        if cac_truong_so_khong_hop_le:
            messagebox.showwarning(
                "Thông tin không hợp lệ",
                "Các trường "
                + ", ".join(cac_truong_so_khong_hop_le)
                + " chỉ được chứa chữ số.",
                parent=doi_tuong.cua_so_goc,
            )
            return

        try:
            with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
                ket_noi.execute(
                    "INSERT INTO khachhang (makh, hoten, cccd, sodt, gioitinh) VALUES (?, ?, ?, ?, ?)",
                    (ma_khach_hang, ho_ten, cccd, so_dien_thoai, gioi_tinh),
                )
            messagebox.showinfo(
                "Thành công",
                "Thêm khách hàng thành công!",
                parent=doi_tuong.cua_so_goc,
            )
            doi_tuong.tai_du_lieu_khach_hang()
            doi_tuong.xoa_trang_o_nhap()
        except sqlite3.IntegrityError as loi:
            thong_bao_loi = str(loi)
            if "khachhang.makh" in thong_bao_loi:
                messagebox.showerror(
                    "Mã khách hàng bị trùng",
                    "Mã khách hàng đã tồn tại. Vui lòng nhập mã khác.",
                    parent=doi_tuong.cua_so_goc,
                )
            elif "idx_khachhang_cccd_unique" in thong_bao_loi or "cccd" in thong_bao_loi:
                messagebox.showerror(
                    "CCCD/CMND bị trùng",
                    "Số CCCD/CMND này đã được đăng ký cho khách hàng khác.",
                    parent=doi_tuong.cua_so_goc,
                )
            else:
                messagebox.showerror("Lỗi dữ liệu", thong_bao_loi, parent=doi_tuong.cua_so_goc)
        except Exception as loi:
            messagebox.showerror("Lỗi", str(loi), parent=doi_tuong.cua_so_goc)

    def chinh_sua_khach_hang(doi_tuong):
        duoc_chon = doi_tuong.bang_du_lieu.selection()
        if not duoc_chon:
            messagebox.showwarning(
                "Chưa chọn khách hàng",
                "Vui lòng chọn khách hàng cần sửa trong bảng danh sách.",
                parent=doi_tuong.cua_so_goc,
            )
            return
        gia_tri = doi_tuong.bang_du_lieu.item(duoc_chon[0], "values")
        doi_tuong.xoa_trang_o_nhap()
        doi_tuong.ma_khach_hang_dang_sua = gia_tri[0]
        doi_tuong.o_nhap_ma_khach_hang.insert(0, gia_tri[0])
        doi_tuong.o_nhap_ma_khach_hang.configure(state="readonly")
        doi_tuong.o_nhap_ho_ten.insert(0, gia_tri[1])
        doi_tuong.o_nhap_cccd.insert(0, gia_tri[2])
        doi_tuong.o_nhap_so_dien_thoai.insert(0, gia_tri[3] or "")
        doi_tuong.gioi_tinh_nhap.set(
            gia_tri[4] if gia_tri[4] in ("Nam", "Nữ") else "Nam"
        )
        doi_tuong.o_nhap_ho_ten.focus_set()

    def luu_khach_hang(doi_tuong):
        if doi_tuong.ma_khach_hang_dang_sua is None:
            messagebox.showwarning(
                "Chưa chọn khách hàng",
                "Vui lòng chọn một khách hàng trong bảng trước khi lưu thay đổi.",
                parent=doi_tuong.cua_so_goc,
            )
            return

        ho_ten = doi_tuong.o_nhap_ho_ten.get().strip()
        cccd = doi_tuong.o_nhap_cccd.get().strip()
        so_dien_thoai = doi_tuong.o_nhap_so_dien_thoai.get().strip()
        gioi_tinh = doi_tuong.gioi_tinh_nhap.get().strip()

        cac_truong_con_thieu = _cac_truong_khach_hang_con_thieu(
            (doi_tuong.ma_khach_hang_dang_sua, ho_ten, cccd, so_dien_thoai, gioi_tinh)
        )
        if cac_truong_con_thieu:
            messagebox.showwarning(
                "Thiếu thông tin",
                "Vui lòng nhập đầy đủ thông tin khách hàng. Còn thiếu: "
                + ", ".join(cac_truong_con_thieu)
                + ".",
                parent=doi_tuong.cua_so_goc,
            )
            return

        cac_truong_so_khong_hop_le = _cac_truong_so_khong_hop_le(
            cccd, so_dien_thoai
        )
        if cac_truong_so_khong_hop_le:
            messagebox.showwarning(
                "Thông tin không hợp lệ",
                "Các trường "
                + ", ".join(cac_truong_so_khong_hop_le)
                + " chỉ được chứa chữ số.",
                parent=doi_tuong.cua_so_goc,
            )
            return

        try:
            with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
                ket_noi.execute(
                    "UPDATE khachhang SET hoten=?, cccd=?, sodt=?, gioitinh=? WHERE makh=?",
                    (
                        ho_ten,
                        cccd,
                        so_dien_thoai,
                        gioi_tinh,
                        doi_tuong.ma_khach_hang_dang_sua,
                    ),
                )
            messagebox.showinfo(
                "Thành công",
                "Cập nhật thông tin khách hàng thành công!",
                parent=doi_tuong.cua_so_goc,
            )
            doi_tuong.tai_du_lieu_khach_hang()
            doi_tuong.xoa_trang_o_nhap()
        except sqlite3.IntegrityError as loi:
            if "idx_khachhang_cccd_unique" in str(loi) or "cccd" in str(loi):
                messagebox.showerror(
                    "CCCD/CMND bị trùng",
                    "Số CCCD/CMND này đã thuộc về khách hàng khác.",
                    parent=doi_tuong.cua_so_goc,
                )
            else:
                messagebox.showerror("Lỗi dữ liệu", str(loi), parent=doi_tuong.cua_so_goc)
        except Exception as loi:
            messagebox.showerror("Lỗi", str(loi), parent=doi_tuong.cua_so_goc)

    def xoa_khach_hang(doi_tuong):
        duoc_chon = doi_tuong.bang_du_lieu.selection()
        if not duoc_chon:
            messagebox.showwarning(
                "Chưa chọn khách hàng",
                "Vui lòng chọn khách hàng cần xóa.",
                parent=doi_tuong.cua_so_goc,
            )
            return

        ma_kh = doi_tuong.bang_du_lieu.item(duoc_chon[0], "values")[0]
        ten_kh = doi_tuong.bang_du_lieu.item(duoc_chon[0], "values")[1]
        if messagebox.askyesno(
            "Xác nhận xóa",
            f"Bạn có chắc muốn xóa khách hàng '{ten_kh}' ({ma_kh})?",
            parent=doi_tuong.cua_so_goc,
        ):
            try:
                with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
                    ket_noi.execute("DELETE FROM khachhang WHERE makh=?", (ma_kh,))
                messagebox.showinfo(
                    "Thành công",
                    "Đã xóa khách hàng khỏi hệ thống.",
                    parent=doi_tuong.cua_so_goc,
                )
                doi_tuong.tai_du_lieu_khach_hang()
                doi_tuong.xoa_trang_o_nhap()
            except sqlite3.IntegrityError:
                messagebox.showerror(
                    "Không thể xóa",
                    "Khách hàng này đã có lịch sử đặt phòng trong hệ thống nên không thể xóa.",
                    parent=doi_tuong.cua_so_goc,
                )
            except Exception as loi:
                messagebox.showerror("Lỗi", str(loi), parent=doi_tuong.cua_so_goc)


if __name__ == "__main__":
    cua_so_goc = tk.Tk()
    cua_so_goc.title("Quản lý khách hàng - THANHVY  Hotel")
    cua_so_goc.geometry("980x680")
    cua_so_goc.configure(bg=BANG_MAU_KHACH_SAN["nen_chinh"])

    cau_hinh_giao_dien_ttk(cua_so_goc)

    class UngDungGiaLap:
        def __init__(self, root):
            self.cua_so_goc = root
            self.duong_dan_co_so_du_lieu = "QLKS.db"
            for ten, gia_tri in BANG_MAU_KHACH_SAN.items():
                setattr(self, ten, gia_tri)

    vung_chua = tk.Frame(
        cua_so_goc,
        bg=BANG_MAU_KHACH_SAN["nen_chinh"],
        padx=16,
        pady=16,
    )
    vung_chua.pack(fill="both", expand=True)

    app_gia_lap = UngDungGiaLap(cua_so_goc)
    bieu_mau = BieuMauKhachHang(app_gia_lap, vung_chua)
    bieu_mau.tao_giao_dien()
    cua_so_goc.mainloop()