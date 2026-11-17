from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
from Create_DB_QLKS import khoi_tao_co_so_du_lieu
from employee_auth import xac_thuc_dang_nhap
from frm_NhanVien import BieuMauNhanVien
from frm_BaoCao import BieuMauBaoCao, BieuMauBaoCaoCongSuatPhong, BieuMauBaoCaoKhachHang
from frm_DatPhong import BieuMauDatPhong
from frm_KhachHang import BieuMauKhachHang
from frm_LoaiPhong import BieuMauLoaiPhong
from frm_Phong import BieuMauPhong
from frm_DichVu import BieuMauSuDungDichVu
from frm_TrangChu import BieuMauTrangChu
from ui_components import (
    BANG_MAU_KHACH_SAN,
    ONhapLieuKhachSan,
    cau_hinh_giao_dien_ttk,
    tao_nut_khach_san,
)


def can_giua_cua_so(cua_so, chieu_rong, chieu_cao):
    cua_so.update_idletasks()
    rong_man_hinh = cua_so.winfo_screenwidth()
    cao_man_hinh = cua_so.winfo_screenheight()
    x = max(0, (rong_man_hinh - chieu_rong) // 2)
    y = max(0, (cao_man_hinh - chieu_cao) // 2)
    cua_so.geometry(f"{chieu_rong}x{chieu_cao}+{x}+{y}")


class UngDungQuanLyKhachSan:
    def __init__(doi_tuong, cua_so_goc, duong_dan_co_so_du_lieu=None):
        doi_tuong.cua_so_goc = cua_so_goc
        doi_tuong.duong_dan_co_so_du_lieu = (
            Path(duong_dan_co_so_du_lieu)
            if duong_dan_co_so_du_lieu is not None
            else Path(__file__).resolve().with_name("QLKS.db")
        )
        khoi_tao_co_so_du_lieu(str(doi_tuong.duong_dan_co_so_du_lieu), thong_bao=False)

        doi_tuong.cua_so_goc.title("THANHVY Hotel | Quản lý khách sạn")
        chieu_rong_man_hinh = doi_tuong.cua_so_goc.winfo_screenwidth()
        chieu_cao_man_hinh = doi_tuong.cua_so_goc.winfo_screenheight()
        chieu_rong_cua_so = max(600, min(1060, chieu_rong_man_hinh - 40))
        chieu_cao_cua_so = max(450, min(740, chieu_cao_man_hinh - 90))
        can_giua_cua_so(doi_tuong.cua_so_goc, chieu_rong_cua_so, chieu_cao_cua_so)
        doi_tuong.cua_so_goc.minsize(
            min(780, chieu_rong_cua_so), min(520, chieu_cao_cua_so)
        )

        # Đồng bộ bảng màu từ ui_components.py
        for ten, gia_tri in BANG_MAU_KHACH_SAN.items():
            setattr(doi_tuong, ten, gia_tri)

        doi_tuong.nhan_vien_hien_tai = None
        doi_tuong.cua_so_goc.configure(bg=doi_tuong.nen_chinh)
        cau_hinh_giao_dien_ttk(doi_tuong.cua_so_goc)

        doi_tuong.khung_ung_dung = tk.Frame(doi_tuong.cua_so_goc, bg=doi_tuong.nen_chinh)

        # Thanh tiêu đề thương hiệu phía trên
        thanh_tren = tk.Frame(
            doi_tuong.khung_ung_dung, bg=doi_tuong.dieu_huong_nen, height=58
        )
        thanh_tren.pack(side="top", fill="x")
        thanh_tren.pack_propagate(False)

        tk.Label(
            thanh_tren,
            text="THANHVY",
            bg=doi_tuong.dieu_huong_nen,
            fg="#F1D9A7",
            font=("Arial", 14, "bold"),
        ).pack(side="left", padx=(24, 6))
        tk.Label(
            thanh_tren,
            text="HOTEL  •  QUẢN LÝ KHÁCH SẠN",
            bg=doi_tuong.dieu_huong_nen,
            fg="#D4E0DB",
            font=("Arial", 9),
        ).pack(side="left")

        doi_tuong.nut_dang_xuat = tao_nut_khach_san(
            thanh_tren, "Đăng xuất", doi_tuong.dang_xuat, "#52615D", padx=12
        )
        doi_tuong.nut_dang_xuat.pack(side="right", padx=(0, 16))

        doi_tuong.nhan_cua_so_nguoi_dung = tk.Label(
            thanh_tren,
            text="",
            bg=doi_tuong.dieu_huong_nen,
            fg="#F1D9A7",
            font=("Arial", 9, "bold"),
        )
        doi_tuong.nhan_cua_so_nguoi_dung.pack(side="right", padx=(12, 12))

        # Thanh menu điều hướng
        thanh_thuc_don = tk.Frame(doi_tuong.khung_ung_dung, bg="#E9E5DA", height=38)
        thanh_thuc_don.pack(fill="x")
        thanh_thuc_don.pack_propagate(False)
        doi_tuong.thanh_thuc_don = thanh_thuc_don

        def them_thuc_don(tieu_de, cac_muc):
            thuc_don_dau_tien = not thanh_thuc_don.winfo_children()
            nut = tk.Menubutton(
                thanh_thuc_don,
                text=tieu_de,
                bg="#E9E5DA",
                fg=doi_tuong.van_ban_mau,
                activebackground="#D8D2C5",
                activeforeground=doi_tuong.dieu_huong_nen,
                font=("Arial", 9, "bold"),
                relief="flat",
                bd=0,
                padx=13,
                pady=7,
                cursor="hand2",
            )
            thuc_don = tk.Menu(
                nut,
                tearoff=0,
                bg=doi_tuong.the_nen,
                fg=doi_tuong.van_ban_mau,
                activebackground=doi_tuong.dieu_huong_nen,
                activeforeground="#FFFFFF",
                font=("Arial", 9),
            )
            for nhan_muc, lenh in cac_muc:
                thuc_don.add_command(label=nhan_muc, command=lenh)
            nut.configure(menu=thuc_don)
            nut.pack(side="left", padx=(12 if thuc_don_dau_tien else 0, 0))

        doi_tuong.cac_trang = {}
        doi_tuong.noi_dung_cac_trang = {}
        doi_tuong.cac_vung_ve_trang = {}
        doi_tuong.cac_thanh_cuon_trang = {}
        doi_tuong.trang_dang_mo = None
        doi_tuong.dang_keo_trang = False
        doi_tuong.toa_do_y_keo_trang = 0
        doi_tuong.phan_du_keo_trang = 0

        them_thuc_don(
            "Chương trình",
            [
                ("Trang chủ", lambda: doi_tuong.hien_thi_trang("home")),
                ("Đăng xuất", doi_tuong.dang_xuat),
                ("Thoát", doi_tuong.cua_so_goc.destroy),
            ],
        )
        them_thuc_don(
            "Danh mục",
            [
                ("Nhân viên", doi_tuong.hien_thi_nhan_vien),
                ("Khách hàng", doi_tuong.hien_thi_khach_hang),
                ("Phòng", doi_tuong.hien_thi_phong),
                ("Loại phòng", doi_tuong.hien_thi_loai_phong),
            ],
        )
        them_thuc_don(
            "Nghiệp vụ",
            [
                ("Đặt phòng & Nhận/Trả phòng", doi_tuong.hien_thi_dat_phong),
                ("Sử dụng dịch vụ", doi_tuong.hien_thi_su_dung_dich_vu),
            ],
        )
        them_thuc_don(
            "Báo cáo",
            [
                ("Doanh thu / hóa đơn", doi_tuong.hien_thi_bao_cao_doanh_thu),
                ("Tình trạng & công suất phòng", doi_tuong.hien_thi_bao_cao_cong_suat),
                ("Danh sách khách lưu trú", doi_tuong.hien_thi_bao_cao_khach_hang),
            ],
        )
        them_thuc_don(
            "Giúp đỡ",
            [
                ("Hướng dẫn", doi_tuong.hien_thi_huong_dan),
                (
                    "Thông tin",
                    lambda: messagebox.showinfo(
                        "Thông tin ứng dụng",
                        "THANHVY Hotel - Quản lý khách sạn\n\n"
                        "Ứng dụng máy tính được xây dựng bằng Python, "
                        "giao diện Tkinter và cơ sở dữ liệu SQLite3.\n\n"
                        "Các chức năng chính:\n"
                        "• Quản lý hồ sơ khách hàng.\n"
                        "• Quản lý phòng, loại phòng và giá theo đêm.\n"
                        "• Tạo, chỉnh sửa và hủy đặt phòng; nhận và trả phòng.\n"
                        "• Lập hóa đơn và theo dõi doanh thu.\n\n"
                        "Dữ liệu được lưu trong cơ sở dữ liệu SQLite; "
                        "mặc định là tệp QLKS.db trong thư mục chương trình.",
                        parent=doi_tuong.cua_so_goc,
                    ),
                ),
            ],
        )

        # Khung chứa các trang chức năng
        khung_chua_trang = tk.Frame(
            doi_tuong.khung_ung_dung, bg=doi_tuong.nen_chinh, padx=24, pady=16
        )
        khung_chua_trang.pack(fill="both", expand=True)

        for ten_trang in (
            "home",
            "customers",
            "rooms",
            "room_types",
            "employees",
            "bookings",
            "reports",
            "room_occupancy_report",
            "guest_report",
            
            "services_usage",
        ):
            trang = tk.Frame(khung_chua_trang, bg=doi_tuong.nen_chinh)
            trang.place(relx=0, rely=0, relwidth=1, relheight=1)
            doi_tuong.cac_trang[ten_trang] = trang
            doi_tuong.noi_dung_cac_trang[ten_trang] = doi_tuong._tao_vung_hien_thi_trang(
                ten_trang, trang
            )

        # Khởi tạo các biểu mẫu con theo đúng chữ ký (ung_dung, khung_cha)
        BieuMauTrangChu(doi_tuong, doi_tuong.noi_dung_cac_trang["home"]).tao_giao_dien()

        doi_tuong.bieu_mau_nhan_vien = BieuMauNhanVien(
        doi_tuong, doi_tuong.noi_dung_cac_trang["employees"]
        )
        doi_tuong.bieu_mau_nhan_vien.tao_giao_dien()

        doi_tuong.bieu_mau_khach_hang = BieuMauKhachHang(
            doi_tuong, doi_tuong.noi_dung_cac_trang["customers"]
        )
        doi_tuong.bieu_mau_khach_hang.tao_giao_dien()

        doi_tuong.bieu_mau_phong = BieuMauPhong(
            doi_tuong, doi_tuong.noi_dung_cac_trang["rooms"]
        )
        doi_tuong.bieu_mau_phong.tao_giao_dien()

        doi_tuong.bieu_mau_loai_phong = BieuMauLoaiPhong(
            doi_tuong, doi_tuong.noi_dung_cac_trang["room_types"]
        )
        doi_tuong.bieu_mau_loai_phong.tao_giao_dien()

        doi_tuong.bieu_mau_dat_phong = BieuMauDatPhong(
            doi_tuong, doi_tuong.noi_dung_cac_trang["bookings"]
        )
        doi_tuong.bieu_mau_dat_phong.tao_giao_dien()

        doi_tuong.bao_cao_doanh_thu = BieuMauBaoCao(
            doi_tuong.noi_dung_cac_trang["reports"],
            str(doi_tuong.duong_dan_co_so_du_lieu),
            khoi_tao=False,
        )
        doi_tuong.bao_cao_doanh_thu.tao_giao_dien()

        doi_tuong.bao_cao_cong_suat = BieuMauBaoCaoCongSuatPhong(
            doi_tuong.noi_dung_cac_trang["room_occupancy_report"],
            str(doi_tuong.duong_dan_co_so_du_lieu),
            khoi_tao=False,
        )
        doi_tuong.bao_cao_cong_suat.tao_giao_dien()

        doi_tuong.bao_cao_khach_hang = BieuMauBaoCaoKhachHang(
            doi_tuong.noi_dung_cac_trang["guest_report"],
            str(doi_tuong.duong_dan_co_so_du_lieu),
            khoi_tao=False,
        )
        doi_tuong.bao_cao_khach_hang.tao_giao_dien()
        # Khởi tạo form:
        doi_tuong.bieu_mau_su_dung_dich_vu = BieuMauSuDungDichVu(
        doi_tuong, doi_tuong.noi_dung_cac_trang["services_usage"]
)
        doi_tuong.bieu_mau_su_dung_dich_vu.tao_giao_dien()

        # Sự kiện cuộn chuột và kéo vùng trang
        doi_tuong.cua_so_goc.bind_all("<MouseWheel>", doi_tuong._cuon_trang_dang_mo)
        doi_tuong.cua_so_goc.bind_all(
            "<Button-4>", lambda su_kien: doi_tuong._cuon_trang_dang_mo(su_kien, -3)
        )
        doi_tuong.cua_so_goc.bind_all(
            "<Button-5>", lambda su_kien: doi_tuong._cuon_trang_dang_mo(su_kien, 3)
        )
        for nut in (2, 3):
            so_thu_tu = str(nut)
            doi_tuong.cua_so_goc.bind_all(
                f"<ButtonPress-{so_thu_tu}>", doi_tuong._bat_dau_keo_trang
            )
            doi_tuong.cua_so_goc.bind_all(
                f"<B{so_thu_tu}-Motion>", doi_tuong._di_chuyen_vung_keo_trang
            )
            doi_tuong.cua_so_goc.bind_all(
                f"<ButtonRelease-{so_thu_tu}>", doi_tuong._ket_thuc_keo_trang
            )
        doi_tuong.cua_so_goc.bind("<Destroy>", doi_tuong._tha_vung_keo_trang, add="+")

        doi_tuong._tao_man_hinh_dang_nhap()

    def _tao_man_hinh_dang_nhap(doi_tuong):
        doi_tuong.khung_dang_nhap = tk.Frame(
            doi_tuong.cua_so_goc, bg=doi_tuong.nen_chinh
        )
        the = tk.Frame(
            doi_tuong.khung_dang_nhap,
            bg=doi_tuong.the_nen,
            padx=40,
            pady=34,
            highlightthickness=1,
            highlightbackground=BANG_MAU_KHACH_SAN["vien_the"],
        )
        the.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            the,
            text="THANHVY  HOTEL",
            bg=doi_tuong.the_nen,
            fg=doi_tuong.nhan_manh_mau,
            font=("Arial", 11, "bold"),
        ).pack(pady=(0, 8))
        tk.Label(
            the,
            text="ĐĂNG NHẬP NHÂN VIÊN",
            bg=doi_tuong.the_nen,
            fg=doi_tuong.dieu_huong_nen,
            font=("Arial", 20, "bold"),
        ).pack(pady=(0, 8))
        tk.Label(
            the,
            text="Vui lòng đăng nhập để sử dụng hệ thống quản lý",
            bg=doi_tuong.the_nen,
            fg=doi_tuong.phu_mau,
            font=("Arial", 10),
        ).pack(pady=(0, 24))

        tk.Label(
            the,
            text="Tên đăng nhập",
            bg=doi_tuong.the_nen,
            fg=doi_tuong.van_ban_mau,
            font=("Arial", 9, "bold"),
        ).pack(anchor="w", pady=(0, 4))
        doi_tuong.o_nhap_ten_dang_nhap = ONhapLieuKhachSan(the, width=38)
        doi_tuong.o_nhap_ten_dang_nhap.pack(fill="x", pady=(0, 12))

        tk.Label(
            the,
            text="Mật khẩu",
            bg=doi_tuong.the_nen,
            fg=doi_tuong.van_ban_mau,
            font=("Arial", 9, "bold"),
        ).pack(anchor="w", pady=(0, 4))
        doi_tuong.o_nhap_mat_khau = ONhapLieuKhachSan(the, width=38, show="•")
        doi_tuong.o_nhap_mat_khau.pack(fill="x", pady=(0, 6))

        doi_tuong.hien_mat_khau = tk.BooleanVar(value=False)
        tk.Checkbutton(
            the,
            text="Hiện mật khẩu",
            variable=doi_tuong.hien_mat_khau,
            command=lambda: doi_tuong.o_nhap_mat_khau.configure(
                show="" if doi_tuong.hien_mat_khau.get() else "•"
            ),
            bg=doi_tuong.the_nen,
            fg=doi_tuong.phu_mau,
            activebackground=doi_tuong.the_nen,
            selectcolor=doi_tuong.the_nen,
            font=("Arial", 9),
            cursor="hand2",
        ).pack(anchor="w", pady=(0, 16))

        doi_tuong.o_nhap_ten_dang_nhap.bind(
            "<Return>", lambda _: doi_tuong.o_nhap_mat_khau.focus_set()
        )
        doi_tuong.o_nhap_mat_khau.bind("<Return>", lambda _: doi_tuong.dang_nhap())

        tao_nut_khach_san(
            the, "ĐĂNG NHẬP", doi_tuong.dang_nhap, doi_tuong.dieu_huong_nen, padx=16
        ).pack(fill="x")

        doi_tuong.khung_ung_dung.pack_forget()
        doi_tuong.khung_dang_nhap.pack(fill="both", expand=True)
        doi_tuong.o_nhap_ten_dang_nhap.focus_set()

    def dang_nhap(doi_tuong):
        nhan_vien = xac_thuc_dang_nhap(
            doi_tuong.o_nhap_ten_dang_nhap.get(),
            doi_tuong.o_nhap_mat_khau.get(),
            doi_tuong.duong_dan_co_so_du_lieu,
        )
        if nhan_vien is None:
            doi_tuong.o_nhap_mat_khau.delete(0, "end")
            messagebox.showerror(
                "Đăng nhập thất bại",
                "Tên đăng nhập hoặc mật khẩu không chính xác.",
                parent=doi_tuong.cua_so_goc,
            )
            doi_tuong.o_nhap_mat_khau.focus_set()
            return

        doi_tuong.nhan_vien_hien_tai = nhan_vien
        doi_tuong.nhan_cua_so_nguoi_dung.configure(
            text=f"Xin chào, {nhan_vien['hoten']} ({nhan_vien['chucvu']})"
        )
        doi_tuong.khung_dang_nhap.pack_forget()
        doi_tuong.khung_ung_dung.pack(fill="both", expand=True)
        doi_tuong.hien_thi_trang("home")
        doi_tuong.o_nhap_mat_khau.delete(0, "end")

    def dang_xuat(doi_tuong):
        doi_tuong.nhan_vien_hien_tai = None
        doi_tuong.nhan_cua_so_nguoi_dung.configure(text="")
        doi_tuong.khung_ung_dung.pack_forget()
        if hasattr(doi_tuong, "khung_dang_nhap"):
            doi_tuong.khung_dang_nhap.pack(fill="both", expand=True)
            doi_tuong.o_nhap_ten_dang_nhap.delete(0, "end")
            doi_tuong.o_nhap_mat_khau.delete(0, "end")
            doi_tuong.hien_mat_khau.set(False)
            doi_tuong.o_nhap_mat_khau.configure(show="•")
            doi_tuong.o_nhap_ten_dang_nhap.focus_set()

    def hien_thi_trang(doi_tuong, ten_trang):
        if ten_trang == "customers":
            doi_tuong.hien_thi_khach_hang()
            return
        if ten_trang == "rooms":
            doi_tuong.hien_thi_phong()
            return
        if ten_trang == "room_types":
            doi_tuong.hien_thi_loai_phong()
            return
        if ten_trang == "bookings":
            doi_tuong.hien_thi_dat_phong()
            return
        doi_tuong._mo_khung_trang(ten_trang)

    def _mo_khung_trang(doi_tuong, ten_trang):
        trang = doi_tuong.cac_trang.get(ten_trang)
        if trang is not None:
            doi_tuong.trang_dang_mo = ten_trang
            trang.tkraise()
            doi_tuong.cac_vung_ve_trang[ten_trang].yview_moveto(0)
            doi_tuong.cua_so_goc.after_idle(
                lambda: doi_tuong._cap_nhat_thanh_cuon_trang(ten_trang)
            )

    def hien_thi_nhan_vien(doi_tuong):
        doi_tuong.bieu_mau_nhan_vien.tai_du_lieu_nhan_vien()
        doi_tuong._mo_khung_trang("employees")

    def hien_thi_khach_hang(doi_tuong):
        doi_tuong.bieu_mau_khach_hang.tai_du_lieu_khach_hang()
        doi_tuong._mo_khung_trang("customers")

    def hien_thi_phong(doi_tuong):
        doi_tuong.bieu_mau_phong.tai_danh_sach_loai_phong()
        doi_tuong.bieu_mau_phong.tai_du_lieu_phong()
        doi_tuong._mo_khung_trang("rooms")

    def hien_thi_loai_phong(doi_tuong):
        doi_tuong.bieu_mau_loai_phong.tai_du_lieu_loai_phong()
        doi_tuong._mo_khung_trang("room_types")

    def hien_thi_dat_phong(doi_tuong):
        doi_tuong.bieu_mau_dat_phong.tai_du_lieu_nguon()
        doi_tuong.bieu_mau_dat_phong.tai_du_lieu_dat_phong()
        doi_tuong._mo_khung_trang("bookings")

    def hien_thi_su_dung_dich_vu(doi_tuong):
        doi_tuong.bieu_mau_su_dung_dich_vu.tai_du_lieu_su_dung_dich_vu()
        doi_tuong._mo_khung_trang("services_usage")

    def hien_thi_bao_cao_doanh_thu(doi_tuong):
        if hasattr(doi_tuong, "bao_cao_doanh_thu") and getattr(
            doi_tuong.bao_cao_doanh_thu, "tai_lai_danh_sach", None
        ):
            doi_tuong.bao_cao_doanh_thu.tai_lai_danh_sach()
        doi_tuong._mo_khung_trang("reports")

    def hien_thi_bao_cao_cong_suat(doi_tuong):
        if hasattr(doi_tuong, "bao_cao_cong_suat") and getattr(
            doi_tuong.bao_cao_cong_suat, "tai_lai_danh_sach", None
        ):
            doi_tuong.bao_cao_cong_suat.tai_lai_danh_sach()
        doi_tuong._mo_khung_trang("room_occupancy_report")

    def hien_thi_bao_cao_khach_hang(doi_tuong):
        if hasattr(doi_tuong, "bao_cao_khach_hang") and getattr(
            doi_tuong.bao_cao_khach_hang, "tai_lai_danh_sach", None
        ):
            doi_tuong.bao_cao_khach_hang.tai_lai_danh_sach()
        doi_tuong._mo_khung_trang("guest_report")

    def _cuon_trang_dang_mo(doi_tuong, su_kien, so_buoc_chi_dinh=None):
        if doi_tuong.trang_dang_mo is None:
            return
        thanh_phan_giao_dien = su_kien.widget
        while thanh_phan_giao_dien is not None:
            if isinstance(thanh_phan_giao_dien, ttk.Treeview):
                return
            thanh_phan_giao_dien = getattr(thanh_phan_giao_dien, "master", None)

        vung_ve = doi_tuong.cac_vung_ve_trang[doi_tuong.trang_dang_mo]
        if so_buoc_chi_dinh is None:
            do_lech = getattr(su_kien, "delta", 0)
            if not do_lech:
                return
            so_buoc = int(do_lech / 120) or (1 if do_lech > 0 else -1)
            vung_ve.yview_scroll(-so_buoc, "units")
        else:
            vung_ve.yview_scroll(so_buoc_chi_dinh, "units")
        return "break"

    def _bat_dau_keo_trang(doi_tuong, su_kien):
        if doi_tuong.trang_dang_mo is None:
            return
        thanh_phan_giao_dien = doi_tuong.cua_so_goc.winfo_containing(
            su_kien.x_root, su_kien.y_root
        )
        khung_dang_hoat_dong = doi_tuong.cac_trang[doi_tuong.trang_dang_mo]
        while (
            thanh_phan_giao_dien is not None
            and thanh_phan_giao_dien is not khung_dang_hoat_dong
        ):
            thanh_phan_giao_dien = getattr(thanh_phan_giao_dien, "master", None)
        if thanh_phan_giao_dien is None:
            return
        doi_tuong.dang_keo_trang = True
        doi_tuong.toa_do_y_keo_trang = su_kien.y_root
        doi_tuong.phan_du_keo_trang = 0
        doi_tuong.cua_so_goc.grab_set()
        return "break"

    def _di_chuyen_vung_keo_trang(doi_tuong, su_kien):
        if not doi_tuong.dang_keo_trang or doi_tuong.trang_dang_mo is None:
            return
        vung_ve = doi_tuong.cac_vung_ve_trang[doi_tuong.trang_dang_mo]
        doi_tuong.phan_du_keo_trang += doi_tuong.toa_do_y_keo_trang - su_kien.y_root
        doi_tuong.toa_do_y_keo_trang = su_kien.y_root
        so_buoc = int(doi_tuong.phan_du_keo_trang / 35)
        if so_buoc:
            vung_ve.yview_scroll(so_buoc, "units")
            doi_tuong.phan_du_keo_trang -= so_buoc * 35
        return "break"

    def _ket_thuc_keo_trang(doi_tuong, _):
        if doi_tuong.dang_keo_trang:
            doi_tuong.dang_keo_trang = False
            doi_tuong._tha_vung_keo_trang()
            return "break"

    def _tha_vung_keo_trang(doi_tuong, _=None):
        if doi_tuong.cua_so_goc.grab_current() is doi_tuong.cua_so_goc:
            doi_tuong.cua_so_goc.grab_release()

    def _tao_vung_hien_thi_trang(doi_tuong, ten_trang, trang):
        vung_ve = tk.Canvas(trang, bg=doi_tuong.nen_chinh, highlightthickness=0)
        thanh_cuon = ttk.Scrollbar(
            trang,
            orient="vertical",
            command=vung_ve.yview,
            style="Hotel.Vertical.TScrollbar",
        )
        vung_ve.configure(yscrollcommand=thanh_cuon.set)
        vung_ve.pack(side="left", fill="both", expand=True)
        noi_dung = tk.Frame(vung_ve, bg=doi_tuong.nen_chinh, padx=18, pady=12)
        vung_cua_so_ve = vung_ve.create_window((0, 0), window=noi_dung, anchor="nw")

        def cap_nhat_vung_cuon(_=None):
            vung_ve.configure(scrollregion=vung_ve.bbox("all"))
            doi_tuong.cua_so_goc.after_idle(
                lambda: doi_tuong._cap_nhat_thanh_cuon_trang(ten_trang)
            )

        noi_dung.bind("<Configure>", cap_nhat_vung_cuon)

        if ten_trang == "home":
            vung_ve.bind(
                "<Configure>",
                lambda su_kien: vung_ve.itemconfigure(
                    vung_cua_so_ve, width=su_kien.width, height=su_kien.height
                ),
            )
        else:
            vung_ve.bind(
                "<Configure>",
                lambda su_kien: vung_ve.itemconfigure(
                    vung_cua_so_ve, width=su_kien.width
                ),
            )

        doi_tuong.cac_vung_ve_trang[ten_trang] = vung_ve
        doi_tuong.cac_thanh_cuon_trang[ten_trang] = thanh_cuon
        return noi_dung

    def _cap_nhat_thanh_cuon_trang(doi_tuong, ten_trang):
        trang = doi_tuong.cac_trang.get(ten_trang)
        vung_ve = doi_tuong.cac_vung_ve_trang.get(ten_trang)
        thanh_cuon = doi_tuong.cac_thanh_cuon_trang.get(ten_trang)
        
        if (
            trang is None
            or vung_ve is None
            or thanh_cuon is None
            or not trang.winfo_ismapped()
        ):
            
            return

        gioi_han = vung_ve.bbox("all")
        if gioi_han is None:
            thanh_cuon.pack_forget()
            return
        chieu_cao_noi_dung = gioi_han[3] - gioi_han[1]
        if chieu_cao_noi_dung > vung_ve.winfo_height() + 1:
            thanh_cuon.pack(side="right", fill="y")
        else:
            thanh_cuon.pack_forget()
            vung_ve.yview_moveto(0)

    def hien_thi_huong_dan(doi_tuong):
        messagebox.showinfo(
            "Hướng dẫn sử dụng",
            "Chọn chức năng trên thanh menu ở đầu cửa sổ:\n\n"
            "• Chương trình > Trang chủ: xem trang giới thiệu đồ án; nhấn "
            "BẮT ĐẦU QUẢN LÝ để mở trang Khách hàng. Đăng xuất trở về màn hình "
            "đăng nhập; Thoát để đóng ứng dụng.\n"
            "• Danh mục > Khách hàng: nhập mã khách hàng, CCCD/CMND, họ tên, "
            "số điện thoại và giới tính để thêm hồ sơ. Chọn khách hàng trong "
            "bảng để chỉnh sửa hoặc xóa; tìm theo mã, tên, CCCD/CMND hoặc "
            "số điện thoại.\n"
            "• Danh mục > Loại phòng: nhập mã loại, tên loại phòng và giá/đêm "
            "để thêm. Chọn loại phòng trong bảng để chỉnh sửa hoặc xóa; chỉ xóa "
            "được loại phòng chưa được gán cho phòng nào.\n"
            "• Danh mục > Phòng: nhập mã, tên và chọn loại phòng để thêm; chọn "
            "phòng trong bảng để chỉnh sửa hoặc xóa. Phòng đã có lượt đặt không "
            "thể bị xóa.\n"
            "• Nghiệp vụ > Đặt phòng & Nhận/Trả phòng: tạo lượt đặt bằng cách "
            "chọn khách hàng, phòng, ngày nhận, ngày trả và số người; làm thủ "
            "tục nhận phòng (Check-in), hủy đặt hoặc trả phòng & lập hóa đơn.\n"
            "• Báo cáo > Doanh thu / hóa đơn: chọn khoảng ngày rồi nhấn Xem báo "
            "cáo để xem danh sách hóa đơn và tổng doanh thu.\n\n"
            "Các chức năng mở trong cùng cửa sổ ứng dụng.",
            parent=doi_tuong.cua_so_goc,
        )


if __name__ == "__main__":
    cua_so_goc = tk.Tk()
    ung_dung = UngDungQuanLyKhachSan(cua_so_goc)
    cua_so_goc.mainloop()