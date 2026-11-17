import tkinter as tk
from ui_components import tao_nut_khach_san


class BieuMauTrangChu:
    def __init__(doi_tuong, ung_dung, khung_cha):
        doi_tuong.ung_dung = ung_dung
        doi_tuong.khung_cha = khung_cha
        for ten in (
            "nen_chinh",
            "dieu_huong_nen",
            "nhan_manh_mau",
            "van_ban_mau",
            "phu_mau",
            "the_nen",
        ):
            setattr(doi_tuong, ten, getattr(ung_dung, ten))

    def tao_giao_dien(doi_tuong):
        return doi_tuong._hien_thi_trang_chu(doi_tuong.khung_cha)

    def _hien_thi_trang_chu(doi_tuong, khung_cha):
        trang_chu = tk.Frame(khung_cha, bg=doi_tuong.nen_chinh)
        trang_chu.pack(fill="both", expand=True)

        bia = tk.Frame(
            trang_chu,
            bg=doi_tuong.dieu_huong_nen,
            padx=3,
            pady=3,
            highlightthickness=1,
            highlightbackground="#D5C49E",
        )
        # Khung viền xanh tự động co giãn theo toàn bộ màn hình khi phóng to
        bia.pack(fill="both", expand=True, padx=15, pady=15)
        
        noi_dung = tk.Frame(bia, bg=doi_tuong.the_nen, padx=36, pady=20)
        noi_dung.pack(fill="both", expand=True)

        tk.Label(
            noi_dung,
            text="THANHVY  H O T E L",
            bg=doi_tuong.the_nen,
            fg=doi_tuong.nhan_manh_mau,
            font=("Arial", 10, "bold"),
        ).pack(pady=(4, 12))
        tk.Label(
            noi_dung,
            text="BÁO CÁO ĐỒ ÁN",
            bg=doi_tuong.the_nen,
            fg=doi_tuong.dieu_huong_nen,
            font=("Arial", 25, "bold"),
        ).pack()
        tk.Label(
            noi_dung,
            text="CHUYÊN ĐỀ PYTHON  •  COS525",
            bg=doi_tuong.the_nen,
            fg=doi_tuong.phu_mau,
            font=("Arial", 11, "bold"),
        ).pack(pady=(5, 16))

        tk.Frame(noi_dung, bg="#D7C59D", height=2).pack(fill="x", padx=80, pady=(0, 16))
        tk.Label(
            noi_dung,
            text="ĐỀ TÀI",
            bg=doi_tuong.the_nen,
            fg=doi_tuong.nhan_manh_mau,
            font=("Arial", 9, "bold"),
        ).pack(pady=(0, 5))
        tk.Label(
            noi_dung,
            text="XÂY DỰNG ỨNG DỤNG QUẢN LÝ KHÁCH SẠN\n"
            "VỚI PYTHON, TKINTER VÀ SQLITE3",
            bg=doi_tuong.the_nen,
            fg=doi_tuong.dieu_huong_nen,
            font=("Arial", 16, "bold"),
            justify="center",
            wraplength=800,
        ).pack(pady=(0, 16))

        tk.Label(
            noi_dung,
            text="GIẢNG VIÊN HƯỚNG DẪN",
            bg=doi_tuong.the_nen,
            fg=doi_tuong.phu_mau,
            font=("Arial", 9, "bold"),
        ).pack()
        tk.Label(
            noi_dung,
            text="ThS. Nguyễn Ngọc Minh  •  Khoa CNTT  •  Trường ĐHAG",
            bg=doi_tuong.the_nen,
            fg=doi_tuong.van_ban_mau,
            font=("Arial", 10),
        ).pack(pady=(3, 5))
        tk.Label(
            noi_dung,
            text="SINH VIÊN THỰC HIỆN",
            bg=doi_tuong.the_nen,
            fg=doi_tuong.phu_mau,
            font=("Arial", 9, "bold"),
        ).pack(pady=(3, 12))

        cac_sinh_vien = tk.Frame(noi_dung, bg=doi_tuong.the_nen)
        cac_sinh_vien.pack()
        for ten, ma_sinh_vien in (
            ("Đặng Nguyễn Thiên Thanh", "DTH245883"),
            ("Nguyễn Thị Thúy Vy", "DTH245955"),
        ):
            sinh_vien = tk.Frame(
                cac_sinh_vien,
                bg="#F4F2ED",
                padx=18,
                pady=9,
                highlightthickness=1,
                highlightbackground="#E6E1D6",
            )
            sinh_vien.pack(side="left", padx=6)
            tk.Label(
                sinh_vien,
                text=ten,
                bg="#F4F2ED",
                fg=doi_tuong.dieu_huong_nen,
                font=("Arial", 10, "bold"),
            ).pack()
            tk.Label(
                sinh_vien,
                text=f"MSSV: {ma_sinh_vien}",
                bg="#F4F2ED",
                fg=doi_tuong.phu_mau,
                font=("Arial", 9),
            ).pack(pady=(3, 0))

        tk.Label(
            noi_dung,
            text="CƠ SỞ DỮ LIỆU: QLKS.db (SQLite3)",
            bg=doi_tuong.the_nen,
            fg=doi_tuong.phu_mau,
            font=("Arial", 9, "italic"),
        ).pack(pady=(12, 7))
        tao_nut_khach_san(
            noi_dung,
            "BẮT ĐẦU QUẢN LÝ",
            lambda: doi_tuong.ung_dung.hien_thi_trang("customers"),
            doi_tuong.dieu_huong_nen,
            padx=18,
        ).pack()
        return trang_chu