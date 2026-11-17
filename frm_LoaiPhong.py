import sqlite3
import tkinter as tk
from tkinter import messagebox
import unicodedata
from db_connection import mo_ket_noi_co_so_du_lieu
from ui_components import (
    BANG_MAU_KHACH_SAN,
    ONhapLieuKhachSan,
    cau_hinh_giao_dien_ttk,
    tao_bang_du_lieu,
    tao_nut_khach_san,
    xoa_du_lieu_bang,
)


def khoa_loai_phong(ten):
    da_chuan_hoa = unicodedata.normalize("NFKC", ten)
    return " ".join(da_chuan_hoa.split()).casefold()


class BieuMauLoaiPhong:
    def __init__(doi_tuong, ung_dung, khung_cha):
        doi_tuong.cua_so_goc = ung_dung.cua_so_goc
        doi_tuong.duong_dan_co_so_du_lieu = getattr(
            ung_dung, "duong_dan_co_so_du_lieu", None
        )
        doi_tuong.khung_cha = khung_cha
        doi_tuong.ma_loai_dang_sua = None
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
            text="Quản lý loại phòng",
            font=("Arial", 22, "bold"),
            fg=doi_tuong.dieu_huong_nen,
            bg=doi_tuong.nen_chinh,
        ).pack(anchor="w")
        tk.Label(
            dau_trang,
            text="Thiết lập danh mục hạng phòng và bảng giá niêm yết theo đêm",
            font=("Arial", 10),
            fg=doi_tuong.phu_mau,
            bg=doi_tuong.nen_chinh,
        ).pack(anchor="w", pady=(4, 0))

        # Khung nhập liệu
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
            text="THÔNG TIN LOẠI PHÒNG",
            font=("Arial", 10, "bold"),
            fg=doi_tuong.nhan_manh_mau,
            bg=doi_tuong.the_nen,
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        nhan_kieu = {
            "bg": doi_tuong.the_nen,
            "fg": doi_tuong.phu_mau,
            "font": ("Arial", 9, "bold"),
        }
        cac_truong = (
            ("Mã loại phòng", "o_nhap_ma_loai", 0),
            ("Tên loại phòng", "o_nhap_ten_loai", 1),
            ("Giá phòng / đêm (VNĐ)", "o_nhap_gia_phong", 2),
        )
        for nhan, thuoc_tinh, cot in cac_truong:
            tk.Label(khung_thong_tin, text=nhan, **nhan_kieu).grid(
                row=1, column=cot, padx=(0, 14), pady=(4, 2), sticky="w"
            )
            o_nhap = ONhapLieuKhachSan(khung_thong_tin)
            setattr(doi_tuong, thuoc_tinh, o_nhap)
            o_nhap.grid(row=2, column=cot, padx=(0, 14), pady=(0, 6), sticky="ew")
            khung_thong_tin.grid_columnconfigure(cot, weight=1)

        # Thanh nút bấm CRUD
        cac_thao_tac = tk.Frame(noi_dung, bg=doi_tuong.nen_chinh)
        cac_thao_tac.pack(fill="x", pady=14)
        tao_nut_khach_san(
            cac_thao_tac,
            "Thêm loại phòng",
            doi_tuong.them_loai_phong,
            doi_tuong.dieu_huong_nen,
        ).pack(side="left", padx=(0, 8))
        tao_nut_khach_san(
            cac_thao_tac,
            "Lưu thay đổi",
            doi_tuong.luu_loai_phong,
            doi_tuong.nhan_manh_mau,
        ).pack(side="left", padx=4)
        tao_nut_khach_san(
            cac_thao_tac,
            "Chỉnh sửa",
            doi_tuong.chinh_sua_loai_phong,
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
            "Xóa loại phòng",
            doi_tuong.xoa_loai_phong,
            "#B91C1C",
        ).pack(side="left", padx=4)

        # Bảng danh sách loại phòng
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
        o_tim.bind("<Return>", lambda _: doi_tuong.tai_du_lieu_loai_phong())

        tao_nut_khach_san(
            khung_tim,
            "Tìm kiếm",
            doi_tuong.tai_du_lieu_loai_phong,
            doi_tuong.dieu_huong_nen,
            padx=12,
        ).pack(side="left", padx=(8, 4))
        tao_nut_khach_san(
            khung_tim,
            "Làm mới",
            lambda: (
                doi_tuong.tu_khoa_tim_kiem.set(""),
                doi_tuong.tai_du_lieu_loai_phong(),
            ),
            "#475569",
            padx=12,
        ).pack(side="left", padx=4)

        doi_tuong.bang_du_lieu = tao_bang_du_lieu(
            the_bang,
            ("maloai", "tenloai", "giaphong", "so_phong"),
            ("Mã loại", "Tên loại phòng", "Giá phòng / đêm", "Số lượng phòng"),
            (130, 320, 200, 160),
            ("center", "w", "e", "center"),
            mau_nen=doi_tuong.the_nen,
        )

        def khi_chon_dong(event=None):
            duoc_chon = doi_tuong.bang_du_lieu.selection()
            if not duoc_chon:
                return
            gia_tri = doi_tuong.bang_du_lieu.item(duoc_chon[0], "values")
            doi_tuong.xoa_trang_o_nhap()
            doi_tuong.ma_loai_dang_sua = gia_tri[0]
            doi_tuong.o_nhap_ma_loai.insert(0, gia_tri[0])
            doi_tuong.o_nhap_ma_loai.configure(state="readonly")
            doi_tuong.o_nhap_ten_loai.insert(0, gia_tri[1])
            gia_so = str(gia_tri[2]).replace(",", "").replace(" đ", "").strip()
            doi_tuong.o_nhap_gia_phong.insert(0, gia_so)

        doi_tuong.bang_du_lieu.bind("<<TreeviewSelect>>", khi_chon_dong)
        doi_tuong.tai_du_lieu_loai_phong()
        return noi_dung

    def xoa_trang_o_nhap(doi_tuong):
        doi_tuong.o_nhap_ma_loai.configure(state="normal")
        doi_tuong.o_nhap_ma_loai.delete(0, tk.END)
        doi_tuong.o_nhap_ten_loai.delete(0, tk.END)
        doi_tuong.o_nhap_gia_phong.delete(0, tk.END)
        doi_tuong.ma_loai_dang_sua = None

    def tai_du_lieu_loai_phong(doi_tuong):
        xoa_du_lieu_bang(doi_tuong.bang_du_lieu)
        tu_khoa = doi_tuong.tu_khoa_tim_kiem.get().strip()
        with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
            cau_truy_van = """
                SELECT lp.maloai, lp.tenloai, lp.giaphong, COUNT(p.maphong) AS so_phong
                FROM loaiphong lp
                LEFT JOIN phong p ON p.maloai = lp.maloai
            """
            if tu_khoa:
                tham_so = f"%{tu_khoa}%"
                cac_dong = ket_noi.execute(
                    cau_truy_van
                    + " WHERE lp.maloai LIKE ? OR lp.tenloai LIKE ? GROUP BY lp.maloai ORDER BY lp.maloai",
                    (tham_so, tham_so),
                ).fetchall()
            else:
                cac_dong = ket_noi.execute(
                    cau_truy_van + " GROUP BY lp.maloai ORDER BY lp.maloai"
                ).fetchall()

        for chi_so, dong in enumerate(cac_dong):
            nhan = "dong_chan" if chi_so % 2 == 0 else "dong_le"
            doi_tuong.bang_du_lieu.insert(
                "",
                tk.END,
                values=(
                    dong["maloai"],
                    dong["tenloai"],
                    f"{dong['giaphong']:,.0f} đ",
                    f"{dong['so_phong']} phòng",
                ),
                tags=(nhan,),
            )

    def _kiem_tra_du_lieu_nhap(doi_tuong, ma_loai, ten_loai, gia_chuoi):
        if not ma_loai or not ten_loai or not gia_chuoi:
            messagebox.showwarning(
                "Thiếu thông tin",
                "Vui lòng nhập đầy đủ Mã loại, Tên loại phòng và Giá phòng.",
                parent=doi_tuong.cua_so_goc,
            )
            return None
        gia_sach = gia_chuoi.replace(",", "").replace(".", "")
        if not gia_sach.isdigit():
            messagebox.showwarning(
                "Giá không hợp lệ",
                "Giá phòng phải là số nguyên không âm.",
                parent=doi_tuong.cua_so_goc,
            )
            return None
        return int(gia_sach)

    def them_loai_phong(doi_tuong):
        if doi_tuong.ma_loai_dang_sua is not None:
            messagebox.showwarning(
                "Đang ở chế độ sửa",
                "Vui lòng nhấn 'Hủy nhập' trước khi thêm loại phòng mới.",
                parent=doi_tuong.cua_so_goc,
            )
            return

        ma_loai = doi_tuong.o_nhap_ma_loai.get().strip().upper()
        ten_loai = doi_tuong.o_nhap_ten_loai.get().strip()
        gia_phong = doi_tuong._kiem_tra_du_lieu_nhap(
            ma_loai, ten_loai, doi_tuong.o_nhap_gia_phong.get().strip()
        )
        if gia_phong is None:
            return

        try:
            with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
                ket_noi.execute(
                    "INSERT INTO loaiphong (maloai, tenloai, tenloai_key, giaphong) VALUES (?, ?, ?, ?)",
                    (ma_loai, ten_loai, khoa_loai_phong(ten_loai), gia_phong),
                )
            messagebox.showinfo(
                "Thành công",
                "Thêm loại phòng mới thành công!",
                parent=doi_tuong.cua_so_goc,
            )
            doi_tuong.tai_du_lieu_loai_phong()
            doi_tuong.xoa_trang_o_nhap()
        except sqlite3.IntegrityError as loi:
            thong_bao = str(loi)
            if "loaiphong.maloai" in thong_bao:
                messagebox.showerror(
                    "Trùng mã loại",
                    f"Mã loại phòng '{ma_loai}' đã tồn tại.",
                    parent=doi_tuong.cua_so_goc,
                )
            elif "loaiphong.tenloai_key" in thong_bao:
                messagebox.showerror(
                    "Trùng tên loại phòng",
                    f"Tên loại phòng '{ten_loai}' đã tồn tại trong hệ thống.",
                    parent=doi_tuong.cua_so_goc,
                )
            else:
                messagebox.showerror("Lỗi dữ liệu", thong_bao, parent=doi_tuong.cua_so_goc)

    def chinh_sua_loai_phong(doi_tuong):
        duoc_chon = doi_tuong.bang_du_lieu.selection()
        if not duoc_chon:
            messagebox.showwarning(
                "Chưa chọn dòng",
                "Vui lòng chọn loại phòng cần chỉnh sửa.",
                parent=doi_tuong.cua_so_goc,
            )
            return
        doi_tuong.o_nhap_ten_loai.focus_set()

    def luu_loai_phong(doi_tuong):
        if doi_tuong.ma_loai_dang_sua is None:
            messagebox.showwarning(
                "Chưa chọn loại phòng",
                "Vui lòng chọn loại phòng cần cập nhật từ bảng danh sách.",
                parent=doi_tuong.cua_so_goc,
            )
            return

        ten_loai = doi_tuong.o_nhap_ten_loai.get().strip()
        gia_phong = doi_tuong._kiem_tra_du_lieu_nhap(
            doi_tuong.ma_loai_dang_sua,
            ten_loai,
            doi_tuong.o_nhap_gia_phong.get().strip(),
        )
        if gia_phong is None:
            return

        try:
            with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
                ket_noi.execute(
                    "UPDATE loaiphong SET tenloai = ?, tenloai_key = ?, giaphong = ? WHERE maloai = ?",
                    (
                        ten_loai,
                        khoa_loai_phong(ten_loai),
                        gia_phong,
                        doi_tuong.ma_loai_dang_sua,
                    ),
                )
            messagebox.showinfo(
                "Thành công",
                "Cập nhật loại phòng thành công!",
                parent=doi_tuong.cua_so_goc,
            )
            doi_tuong.tai_du_lieu_loai_phong()
            doi_tuong.xoa_trang_o_nhap()
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Trùng tên loại phòng",
                f"Tên loại phòng '{ten_loai}' đã tồn tại.",
                parent=doi_tuong.cua_so_goc,
            )

    def xoa_loai_phong(doi_tuong):
        duoc_chon = doi_tuong.bang_du_lieu.selection()
        if not duoc_chon:
            messagebox.showwarning(
                "Chưa chọn dòng",
                "Vui lòng chọn loại phòng cần xóa.",
                parent=doi_tuong.cua_so_goc,
            )
            return

        ma_loai, ten_loai = doi_tuong.bang_du_lieu.item(duoc_chon[0], "values")[:2]
        if messagebox.askyesno(
            "Xác nhận xóa",
            f"Bạn có chắc muốn xóa loại phòng '{ten_loai}' ({ma_loai})?",
            parent=doi_tuong.cua_so_goc,
        ):
            try:
                with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
                    ket_noi.execute("DELETE FROM loaiphong WHERE maloai = ?", (ma_loai,))
                messagebox.showinfo(
                    "Thành công",
                    "Đã xóa loại phòng.",
                    parent=doi_tuong.cua_so_goc,
                )
                doi_tuong.tai_du_lieu_loai_phong()
                doi_tuong.xoa_trang_o_nhap()
            except sqlite3.IntegrityError:
                messagebox.showerror(
                    "Không thể xóa",
                    "Đang có phòng thuộc loại phòng này nên không thể xóa.",
                    parent=doi_tuong.cua_so_goc,
                )


if __name__ == "__main__":
    cua_so = tk.Tk()
    cua_so.title("Quản lý loại phòng - Aurelia Hotel")
    cua_so.geometry("960x640")
    cua_so.configure(bg=BANG_MAU_KHACH_SAN["nen_chinh"])
    cau_hinh_giao_dien_ttk(cua_so)

    class UngDungGiaLap:
        cua_so_goc = cua_so
        duong_dan_co_so_du_lieu = "QLKS.db"

    khung = tk.Frame(cua_so, bg=BANG_MAU_KHACH_SAN["nen_chinh"], padx=16, pady=16)
    khung.pack(fill="both", expand=True)
    BieuMauLoaiPhong(UngDungGiaLap(), khung).tao_giao_dien()
    cua_so.mainloop()