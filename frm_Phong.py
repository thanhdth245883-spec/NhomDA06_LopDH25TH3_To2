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


class BieuMauPhong:
    def __init__(doi_tuong, ung_dung, khung_cha):
        doi_tuong.cua_so_goc = ung_dung.cua_so_goc
        doi_tuong.duong_dan_co_so_du_lieu = getattr(
            ung_dung, "duong_dan_co_so_du_lieu", None
        )
        doi_tuong.khung_cha = khung_cha
        doi_tuong.ma_phong_dang_sua = None
        doi_tuong.danh_sach_loai_phong = {}  # { "LP01 - Phòng Đơn...": "LP01" }
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
            text="Quản lý danh sách phòng",
            font=("Arial", 22, "bold"),
            fg=doi_tuong.dieu_huong_nen,
            bg=doi_tuong.nen_chinh,
        ).pack(anchor="w")
        tk.Label(
            dau_trang,
            text="Cập nhật sơ đồ phòng, phân hạng loại phòng và theo dõi tình trạng lưu trú",
            font=("Arial", 10),
            fg=doi_tuong.phu_mau,
            bg=doi_tuong.nen_chinh,
        ).pack(anchor="w", pady=(4, 0))

        # Khung nhập thông tin phòng
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
            text="THÔNG TIN PHÒNG",
            font=("Arial", 10, "bold"),
            fg=doi_tuong.nhan_manh_mau,
            bg=doi_tuong.the_nen,
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        nhan_kieu = {
            "bg": doi_tuong.the_nen,
            "fg": doi_tuong.phu_mau,
            "font": ("Arial", 9, "bold"),
        }

        tk.Label(khung_thong_tin, text="Mã phòng", **nhan_kieu).grid(
            row=1, column=0, padx=(0, 14), pady=(4, 2), sticky="w"
        )
        doi_tuong.o_nhap_ma_phong = ONhapLieuKhachSan(khung_thong_tin)
        doi_tuong.o_nhap_ma_phong.grid(
            row=2, column=0, padx=(0, 14), pady=(0, 6), sticky="ew"
        )

        tk.Label(khung_thong_tin, text="Tên phòng", **nhan_kieu).grid(
            row=1, column=1, padx=(0, 14), pady=(4, 2), sticky="w"
        )
        doi_tuong.o_nhap_ten_phong = ONhapLieuKhachSan(khung_thong_tin)
        doi_tuong.o_nhap_ten_phong.grid(
            row=2, column=1, padx=(0, 14), pady=(0, 6), sticky="ew"
        )

        tk.Label(khung_thong_tin, text="Loại phòng", **nhan_kieu).grid(
            row=1, column=2, padx=(0, 0), pady=(4, 2), sticky="w"
        )
        doi_tuong.hop_chon_loai_phong = OHopChonKhachSan(khung_thong_tin)
        doi_tuong.hop_chon_loai_phong.grid(
            row=2, column=2, padx=(0, 0), pady=(0, 6), sticky="ew"
        )

        for cot in range(3):
            khung_thong_tin.grid_columnconfigure(cot, weight=1)

        # Thanh nút bấm CRUD
        cac_thao_tac = tk.Frame(noi_dung, bg=doi_tuong.nen_chinh)
        cac_thao_tac.pack(fill="x", pady=14)
        tao_nut_khach_san(
            cac_thao_tac,
            "Thêm phòng",
            doi_tuong.them_phong,
            doi_tuong.dieu_huong_nen,
        ).pack(side="left", padx=(0, 8))
        tao_nut_khach_san(
            cac_thao_tac,
            "Lưu thay đổi",
            doi_tuong.luu_phong,
            doi_tuong.nhan_manh_mau,
        ).pack(side="left", padx=4)
        tao_nut_khach_san(
            cac_thao_tac,
            "Chỉnh sửa",
            doi_tuong.chinh_sua_phong,
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
            "Xóa phòng",
            doi_tuong.xoa_phong,
            "#B91C1C",
        ).pack(side="left", padx=4)

        # Khung tìm kiếm & bảng danh sách phòng
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
        o_tim.bind("<Return>", lambda _: doi_tuong.tai_du_lieu_phong())

        tao_nut_khach_san(
            khung_tim,
            "Tìm phòng",
            doi_tuong.tai_du_lieu_phong,
            doi_tuong.dieu_huong_nen,
            padx=12,
        ).pack(side="left", padx=(8, 4))
        tao_nut_khach_san(
            khung_tim,
            "Làm mới",
            lambda: (
                doi_tuong.tu_khoa_tim_kiem.set(""),
                doi_tuong.tai_danh_sach_loai_phong(),
                doi_tuong.tai_du_lieu_phong(),
            ),
            "#475569",
            padx=12,
        ).pack(side="left", padx=4)

        doi_tuong.bang_du_lieu = tao_bang_du_lieu(
            the_bang,
            ("maphong", "tenphong", "tenloai", "giaphong", "tinhtrang"),
            ("Mã phòng", "Tên phòng", "Loại phòng", "Giá niêm yết", "Tình trạng hiện tại"),
            (110, 210, 230, 160, 170),
            ("center", "w", "w", "e", "center"),
            mau_nen=doi_tuong.the_nen,
        )

        def khi_chon_phong(event=None):
            duoc_chon = doi_tuong.bang_du_lieu.selection()
            if not duoc_chon:
                return
            gia_tri = doi_tuong.bang_du_lieu.item(duoc_chon[0], "values")
            doi_tuong.xoa_trang_o_nhap()
            doi_tuong.ma_phong_dang_sua = gia_tri[0]
            doi_tuong.o_nhap_ma_phong.insert(0, gia_tri[0])
            doi_tuong.o_nhap_ma_phong.configure(state="readonly")
            doi_tuong.o_nhap_ten_phong.insert(0, gia_tri[1])

            for nhan_hien_thi in doi_tuong.danh_sach_loai_phong:
                if nhan_hien_thi.endswith(f" - {gia_tri[2]}"):
                    doi_tuong.hop_chon_loai_phong.set(nhan_hien_thi)
                    break

        doi_tuong.bang_du_lieu.bind("<<TreeviewSelect>>", khi_chon_phong)
        doi_tuong.tai_danh_sach_loai_phong()
        doi_tuong.tai_du_lieu_phong()
        return noi_dung

    def tai_danh_sach_loai_phong(doi_tuong):
        doi_tuong.danh_sach_loai_phong.clear()
        with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
            cac_loai = ket_noi.execute(
                "SELECT maloai, tenloai FROM loaiphong ORDER BY maloai"
            ).fetchall()
        cac_nhan = []
        for dong in cac_loai:
            nhan = f"{dong['maloai']} - {dong['tenloai']}"
            doi_tuong.danh_sach_loai_phong[nhan] = dong["maloai"]
            cac_nhan.append(nhan)
        doi_tuong.hop_chon_loai_phong["values"] = cac_nhan
        if cac_nhan and not doi_tuong.hop_chon_loai_phong.get():
            doi_tuong.hop_chon_loai_phong.set(cac_nhan[0])

    def xoa_trang_o_nhap(doi_tuong):
        doi_tuong.o_nhap_ma_phong.configure(state="normal")
        doi_tuong.o_nhap_ma_phong.delete(0, tk.END)
        doi_tuong.o_nhap_ten_phong.delete(0, tk.END)
        cac_nhan = list(doi_tuong.danh_sach_loai_phong.keys())
        doi_tuong.hop_chon_loai_phong.set(cac_nhan[0] if cac_nhan else "")
        doi_tuong.ma_phong_dang_sua = None

    def tai_du_lieu_phong(doi_tuong):
        xoa_du_lieu_bang(doi_tuong.bang_du_lieu)
        tu_khoa = doi_tuong.tu_khoa_tim_kiem.get().strip()
        with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
            cau_truy_van = """
                SELECT
                    p.maphong,
                    p.tenphong,
                    lp.tenloai,
                    lp.giaphong,
                    CASE
                        WHEN EXISTS (
                            SELECT 1 FROM datphong dp
                            WHERE dp.maphong = p.maphong AND dp.trangthai = 'Đang ở'
                        ) THEN 'Đang có khách ở'
                        WHEN EXISTS (
                            SELECT 1 FROM datphong dp
                            WHERE dp.maphong = p.maphong AND dp.trangthai = 'Đã đặt'
                        ) THEN 'Đã được đặt trước'
                        ELSE 'Phòng trống'
                    END AS tinhtrang
                FROM phong p
                JOIN loaiphong lp ON lp.maloai = p.maloai
            """
            if tu_khoa:
                tham_so = f"%{tu_khoa}%"
                cac_dong = ket_noi.execute(
                    cau_truy_van
                    + " WHERE p.maphong LIKE ? OR p.tenphong LIKE ? OR lp.tenloai LIKE ? ORDER BY p.maphong",
                    (tham_so, tham_so, tham_so),
                ).fetchall()
            else:
                cac_dong = ket_noi.execute(
                    cau_truy_van + " ORDER BY p.maphong"
                ).fetchall()

        for chi_so, dong in enumerate(cac_dong):
            nhan = "dong_chan" if chi_so % 2 == 0 else "dong_le"
            doi_tuong.bang_du_lieu.insert(
                "",
                tk.END,
                values=(
                    dong["maphong"],
                    dong["tenphong"],
                    dong["tenloai"],
                    f"{dong['giaphong']:,.0f} đ",
                    dong["tinhtrang"],
                ),
                tags=(nhan,),
            )

    def them_phong(doi_tuong):
        if doi_tuong.ma_phong_dang_sua is not None:
            messagebox.showwarning(
                "Đang ở chế độ sửa",
                "Vui lòng nhấn 'Hủy nhập' trước khi thêm phòng mới.",
                parent=doi_tuong.cua_so_goc,
            )
            return

        ma_phong = doi_tuong.o_nhap_ma_phong.get().strip().upper()
        ten_phong = doi_tuong.o_nhap_ten_phong.get().strip()
        nhan_loai = doi_tuong.hop_chon_loai_phong.get()
        ma_loai = doi_tuong.danh_sach_loai_phong.get(nhan_loai)

        if not ma_phong or not ten_phong or not ma_loai:
            messagebox.showwarning(
                "Thiếu thông tin",
                "Vui lòng nhập Mã phòng, Tên phòng và chọn Loại phòng.",
                parent=doi_tuong.cua_so_goc,
            )
            return

        try:
            with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
                ket_noi.execute(
                    "INSERT INTO phong (maphong, tenphong, maloai) VALUES (?, ?, ?)",
                    (ma_phong, ten_phong, ma_loai),
                )
            messagebox.showinfo(
                "Thành công",
                "Thêm phòng mới thành công!",
                parent=doi_tuong.cua_so_goc,
            )
            doi_tuong.tai_du_lieu_phong()
            doi_tuong.xoa_trang_o_nhap()
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Trùng mã phòng",
                f"Mã phòng '{ma_phong}' đã tồn tại trong hệ thống.",
                parent=doi_tuong.cua_so_goc,
            )

    def chinh_sua_phong(doi_tuong):
        if not doi_tuong.bang_du_lieu.selection():
            messagebox.showwarning(
                "Chưa chọn phòng",
                "Vui lòng chọn phòng cần chỉnh sửa trong danh sách.",
                parent=doi_tuong.cua_so_goc,
            )
            return
        doi_tuong.o_nhap_ten_phong.focus_set()

    def luu_phong(doi_tuong):
        if doi_tuong.ma_phong_dang_sua is None:
            messagebox.showwarning(
                "Chưa chọn phòng",
                "Vui lòng chọn một phòng trong bảng trước khi lưu thay đổi.",
                parent=doi_tuong.cua_so_goc,
            )
            return

        ten_phong = doi_tuong.o_nhap_ten_phong.get().strip()
        ma_loai = doi_tuong.danh_sach_loai_phong.get(
            doi_tuong.hop_chon_loai_phong.get()
        )
        if not ten_phong or not ma_loai:
            messagebox.showwarning(
                "Thiếu thông tin",
                "Vui lòng nhập đầy đủ Tên phòng và Loại phòng.",
                parent=doi_tuong.cua_so_goc,
            )
            return

        with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
            ket_noi.execute(
                "UPDATE phong SET tenphong = ?, maloai = ? WHERE maphong = ?",
                (ten_phong, ma_loai, doi_tuong.ma_phong_dang_sua),
            )
        messagebox.showinfo(
            "Thành công",
            "Cập nhật thông tin phòng thành công!",
            parent=doi_tuong.cua_so_goc,
        )
        doi_tuong.tai_du_lieu_phong()
        doi_tuong.xoa_trang_o_nhap()

    def xoa_phong(doi_tuong):
        duoc_chon = doi_tuong.bang_du_lieu.selection()
        if not duoc_chon:
            messagebox.showwarning(
                "Chưa chọn phòng",
                "Vui lòng chọn phòng cần xóa.",
                parent=doi_tuong.cua_so_goc,
            )
            return

        ma_phong, ten_phong = doi_tuong.bang_du_lieu.item(duoc_chon[0], "values")[:2]
        if messagebox.askyesno(
            "Xác nhận xóa",
            f"Bạn có chắc muốn xóa '{ten_phong}' ({ma_phong})?",
            parent=doi_tuong.cua_so_goc,
        ):
            try:
                with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
                    ket_noi.execute("DELETE FROM phong WHERE maphong = ?", (ma_phong,))
                messagebox.showinfo(
                    "Thành công",
                    "Đã xóa phòng khỏi hệ thống.",
                    parent=doi_tuong.cua_so_goc,
                )
                doi_tuong.tai_du_lieu_phong()
                doi_tuong.xoa_trang_o_nhap()
            except sqlite3.IntegrityError:
                messagebox.showerror(
                    "Không thể xóa",
                    "Phòng này đã có dữ liệu đặt phòng trong lịch sử nên không thể xóa.",
                    parent=doi_tuong.cua_so_goc,
                )


if __name__ == "__main__":
    cua_so = tk.Tk()
    cua_so.title("Quản lý phòng - Aurelia Hotel")
    cua_so.geometry("980x660")
    cua_so.configure(bg=BANG_MAU_KHACH_SAN["nen_chinh"])
    cau_hinh_giao_dien_ttk(cua_so)

    class UngDungGiaLap:
        cua_so_goc = cua_so
        duong_dan_co_so_du_lieu = "QLKS.db"

    khung = tk.Frame(cua_so, bg=BANG_MAU_KHACH_SAN["nen_chinh"], padx=16, pady=16)
    khung.pack(fill="both", expand=True)
    BieuMauPhong(UngDungGiaLap(), khung).tao_giao_dien()
    cua_so.mainloop()