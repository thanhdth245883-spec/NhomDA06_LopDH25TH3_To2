from datetime import date, datetime
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


def _phan_tich_ngay_iso(chuoi_ngay):
    try:
        return datetime.strptime(chuoi_ngay.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None
    
def _lay_chi_tiet_dich_vu_theo_dat_phong(duong_dan_db, dp_id):
    """Lấy tổng tiền và chi tiết dịch vụ của phiếu đặt phòng (chấp nhận mọi biến thể mã)."""
    with mo_ket_noi_co_so_du_lieu(duong_dan_db) as ket_noi:
        co_bang = ket_noi.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='sudungdichvu'"
        ).fetchone()
        if not co_bang:
            return 0.0, []

        cac_cot = [
            r[1] for r in ket_noi.execute("PRAGMA table_info(sudungdichvu)").fetchall()
        ]
        cot_madat = next(
            (
                c
                for c in cac_cot
                if c.lower() in ("madat", "datphong_id", "madp", "madatphong", "ma_dat")
            ),
            "madat",
        )
        cot_tien = next(
            (c for c in cac_cot if c.lower() in ("thanhtien", "thanh_tien", "tongtien")),
            "thanhtien",
        )
        cot_sl = next(
            (c for c in cac_cot if c.lower() in ("soluong", "so_luong", "sl")),
            "soluong",
        )

        # Lấy toàn bộ dòng sử dụng dịch vụ và khớp linh hoạt theo dp_id
        co_bang_dv = ket_noi.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='dichvu'"
        ).fetchone()

        if co_bang_dv:
            tat_ca = ket_noi.execute(
                f"""
                SELECT sddv.{cot_madat} AS ma_dp,
                       COALESCE(dv.tendv, sddv.madv) AS tendv,
                       sddv.{cot_sl} AS soluong,
                       sddv.{cot_tien} AS thanhtien
                FROM sudungdichvu sddv
                LEFT JOIN dichvu dv ON sddv.madv = dv.madv
                ORDER BY sddv.masddv
                """
            ).fetchall()
        else:
            tat_ca = ket_noi.execute(
                f"""
                SELECT {cot_madat} AS ma_dp,
                       madv AS tendv,
                       {cot_sl} AS soluong,
                       {cot_tien} AS thanhtien
                FROM sudungdichvu
                ORDER BY masddv
                """
            ).fetchall()

        id_can_tim = str(dp_id).strip()
        tong_tien = 0.0
        tom_tat = []

        for d in tat_ca:
            gia_tri_ma = str(d["ma_dp"] or "").strip()
            # Khớp chính xác ("1" == "1") hoặc khớp phần đầu trước dấu " - " ("1 - Phòng...")
            ma_tach = gia_tri_ma.split(" - ")[0].strip()
            ma_so = "".join(ch for ch in ma_tach if ch.isdigit())
            if id_can_tim in (gia_tri_ma, ma_tach, ma_so):
                tien = float(d["thanhtien"] or 0.0)
                tong_tien += tien
                tom_tat.append(f"• {d['tendv']} (x{d['soluong']}): {tien:,.0f} đ")

        return tong_tien, tom_tat


class BieuMauDatPhong:
    def __init__(doi_tuong, ung_dung, khung_cha):
        doi_tuong.cua_so_goc = ung_dung.cua_so_goc
        doi_tuong.duong_dan_co_so_du_lieu = getattr(
            ung_dung, "duong_dan_co_so_du_lieu", None
        )
        doi_tuong.khung_cha = khung_cha
        doi_tuong.ban_do_khach_hang = {}
        doi_tuong.ban_do_phong = {}  # { nhan_phong: (maphong, giaphong) }
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
            text="Đặt phòng, Lưu trú & Lập hóa đơn",
            font=("Arial", 22, "bold"),
            fg=doi_tuong.dieu_huong_nen,
            bg=doi_tuong.nen_chinh,
        ).pack(anchor="w")
        tk.Label(
            dau_trang,
            text="Tạo phiếu đặt phòng, làm thủ tục nhận phòng (Check-in) và thanh toán trả phòng (Check-out)",
            font=("Arial", 10),
            fg=doi_tuong.phu_mau,
            bg=doi_tuong.nen_chinh,
        ).pack(anchor="w", pady=(4, 0))

        # Khung tạo phiếu đặt phòng mới
        khung_dat = tk.Frame(
            noi_dung,
            bg=doi_tuong.the_nen,
            padx=20,
            pady=14,
            highlightthickness=1,
            highlightbackground=BANG_MAU_KHACH_SAN["vien_the"],
        )
        khung_dat.pack(fill="x")
        tk.Label(
            khung_dat,
            text="TẠO PHIẾU ĐẶT PHÒNG MỚI",
            font=("Arial", 10, "bold"),
            fg=doi_tuong.nhan_manh_mau,
            bg=doi_tuong.the_nen,
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))

        nhan_kieu = {
            "bg": doi_tuong.the_nen,
            "fg": doi_tuong.phu_mau,
            "font": ("Arial", 9, "bold"),
        }

        # Dòng 1: Khách hàng & Phòng
        tk.Label(khung_dat, text="Khách hàng", **nhan_kieu).grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(2, 2)
        )
        doi_tuong.hop_chon_khach = OHopChonKhachSan(khung_dat)
        doi_tuong.hop_chon_khach.grid(
            row=2, column=0, columnspan=2, padx=(0, 14), pady=(0, 8), sticky="ew"
        )

        tk.Label(khung_dat, text="Phòng & Đơn giá/đêm", **nhan_kieu).grid(
            row=1, column=2, columnspan=2, sticky="w", pady=(2, 2)
        )
        doi_tuong.hop_chon_phong = OHopChonKhachSan(khung_dat)
        doi_tuong.hop_chon_phong.grid(
            row=2, column=2, columnspan=2, pady=(0, 8), sticky="ew"
        )

        # Dòng 2: Ngày nhận, Ngày trả, Số người, Hình thức nhận
        hom_nay = date.today().isoformat()
        ngay_mai = date.fromordinal(date.today().toordinal() + 1).isoformat()

        tk.Label(khung_dat, text="Ngày nhận phòng (YYYY-MM-DD)", **nhan_kieu).grid(
            row=3, column=0, sticky="w", pady=(2, 2)
        )
        doi_tuong.o_ngay_nhan = ONhapLieuKhachSan(khung_dat)
        doi_tuong.o_ngay_nhan.insert(0, hom_nay)
        doi_tuong.o_ngay_nhan.grid(row=4, column=0, padx=(0, 14), pady=(0, 6), sticky="ew")

        tk.Label(khung_dat, text="Ngày trả phòng (YYYY-MM-DD)", **nhan_kieu).grid(
            row=3, column=1, sticky="w", pady=(2, 2)
        )
        doi_tuong.o_ngay_tra = ONhapLieuKhachSan(khung_dat)
        doi_tuong.o_ngay_tra.insert(0, ngay_mai)
        doi_tuong.o_ngay_tra.grid(row=4, column=1, padx=(0, 14), pady=(0, 6), sticky="ew")

        tk.Label(khung_dat, text="Số người ở", **nhan_kieu).grid(
            row=3, column=2, sticky="w", pady=(2, 2)
        )
        doi_tuong.o_so_nguoi = ONhapLieuKhachSan(khung_dat)
        doi_tuong.o_so_nguoi.insert(0, "2")
        doi_tuong.o_so_nguoi.grid(row=4, column=2, padx=(0, 14), pady=(0, 6), sticky="ew")

        tk.Label(khung_dat, text="Hình thức nhận", **nhan_kieu).grid(
            row=3, column=3, sticky="w", pady=(2, 2)
        )
        doi_tuong.hop_trang_thai_moi = OHopChonKhachSan(
            khung_dat, values=("Đã đặt", "Đang ở")
        )
        doi_tuong.hop_trang_thai_moi.set("Đã đặt")
        doi_tuong.hop_trang_thai_moi.grid(row=4, column=3, pady=(0, 6), sticky="ew")

        for cot in range(4):
            khung_dat.grid_columnconfigure(cot, weight=1)

        # Thanh nút nghiệp vụ
        cac_thao_tac = tk.Frame(noi_dung, bg=doi_tuong.nen_chinh)
        cac_thao_tac.pack(fill="x", pady=12)
        tao_nut_khach_san(
            cac_thao_tac,
            "Tạo đặt phòng",
            doi_tuong.tao_dat_phong,
            doi_tuong.dieu_huong_nen,
        ).pack(side="left", padx=(0, 8))
        tao_nut_khach_san(
            cac_thao_tac,
            "Nhận phòng (Check-in)",
            doi_tuong.nhan_phong,
            "#2563EB",
        ).pack(side="left", padx=4)
        tao_nut_khach_san(
            cac_thao_tac,
            "Trả phòng & Lập hóa đơn",
            doi_tuong.mo_hop_thoai_thanh_toan,
            doi_tuong.nhan_manh_mau,
        ).pack(side="left", padx=4)
        tao_nut_khach_san(
            cac_thao_tac,
            "Hủy đặt phòng",
            doi_tuong.huy_dat_phong,
            "#B91C1C",
        ).pack(side="left", padx=4)

        # Khung lọc & bảng danh sách lượt đặt phòng
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
            text="Lọc trạng thái:",
            bg=doi_tuong.the_nen,
            fg=doi_tuong.van_ban_mau,
            font=("Arial", 9, "bold"),
        ).pack(side="left", padx=(0, 6))

        doi_tuong.hop_loc_trang_thai = OHopChonKhachSan(
            khung_loc,
            values=("Tất cả", "Đã đặt", "Đang ở", "Đã trả", "Đã hủy"),
            width=14,
        )
        doi_tuong.hop_loc_trang_thai.set("Tất cả")
        doi_tuong.hop_loc_trang_thai.pack(side="left", padx=(0, 10))
        doi_tuong.hop_loc_trang_thai.bind(
            "<<ComboboxSelected>>", lambda _: doi_tuong.tai_du_lieu_dat_phong()
        )

        doi_tuong.tu_khoa_tim_kiem = tk.StringVar()
        o_tim = ONhapLieuKhachSan(khung_loc, textvariable=doi_tuong.tu_khoa_tim_kiem)
        o_tim.pack(side="left", fill="x", expand=True)
        o_tim.bind("<Return>", lambda _: doi_tuong.tai_du_lieu_dat_phong())

        tao_nut_khach_san(
            khung_loc,
            "Tìm kiếm",
            doi_tuong.tai_du_lieu_dat_phong,
            doi_tuong.dieu_huong_nen,
            padx=12,
        ).pack(side="left", padx=(8, 4))
        tao_nut_khach_san(
            khung_loc,
            "Làm mới",
            lambda: (
                doi_tuong.tu_khoa_tim_kiem.set(""),
                doi_tuong.hop_loc_trang_thai.set("Tất cả"),
                doi_tuong.tai_du_lieu_nguon(),
                doi_tuong.tai_du_lieu_dat_phong(),
            ),
            "#475569",
            padx=12,
        ).pack(side="left", padx=4)

        doi_tuong.bang_du_lieu = tao_bang_du_lieu(
            the_bang,
            ("id", "khachhang", "phong", "ngay_nhan", "ngay_tra", "so_nguoi", "gia_phong", "trangthai", "tong_tt"),
            ("Mã ĐP", "Khách hàng", "Phòng", "Ngày nhận", "Ngày trả", "Khách", "Đơn giá/đêm", "Trạng thái", "Đã thanh toán"),
            (65, 190, 130, 105, 105, 65, 120, 100, 130),
            ("center", "w", "w", "center", "center", "center", "e", "center", "e"),
            mau_nen=doi_tuong.the_nen,
        )

        doi_tuong.tai_du_lieu_nguon()
        doi_tuong.tai_du_lieu_dat_phong()
        return noi_dung

    def tai_du_lieu_nguon(doi_tuong):
        doi_tuong.ban_do_khach_hang.clear()
        doi_tuong.ban_do_phong.clear()
        with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
            cac_kh = ket_noi.execute(
                "SELECT makh, hoten, cccd FROM khachhang ORDER BY makh"
            ).fetchall()
            cac_phong = ket_noi.execute(
                """
                SELECT p.maphong, p.tenphong, lp.tenloai, lp.giaphong
                FROM phong p
                JOIN loaiphong lp ON lp.maloai = p.maloai
                ORDER BY p.maphong
                """
            ).fetchall()

        ds_kh = []
        for kh in cac_kh:
            nhan_kh = f"{kh['makh']} - {kh['hoten']} ({kh['cccd']})"
            doi_tuong.ban_do_khach_hang[nhan_kh] = kh["makh"]
            ds_kh.append(nhan_kh)
        doi_tuong.hop_chon_khach["values"] = ds_kh
        if ds_kh and not doi_tuong.hop_chon_khach.get():
            doi_tuong.hop_chon_khach.set(ds_kh[0])

        ds_phong = []
        for p in cac_phong:
            nhan_phong = f"{p['maphong']} - {p['tenphong']} ({p['tenloai']} • {p['giaphong']:,.0f}đ)"
            doi_tuong.ban_do_phong[nhan_phong] = (p["maphong"], p["giaphong"])
            ds_phong.append(nhan_phong)
        doi_tuong.hop_chon_phong["values"] = ds_phong
        if ds_phong and not doi_tuong.hop_chon_phong.get():
            doi_tuong.hop_chon_phong.set(ds_phong[0])

    def tai_du_lieu_dat_phong(doi_tuong):
        xoa_du_lieu_bang(doi_tuong.bang_du_lieu)
        trang_thai_loc = doi_tuong.hop_loc_trang_thai.get()
        tu_khoa = doi_tuong.tu_khoa_tim_kiem.get().strip()

        dieu_kien = []
        tham_so = []
        if trang_thai_loc and trang_thai_loc != "Tất cả":
            dieu_kien.append("dp.trangthai = ?")
            tham_so.append(trang_thai_loc)
        if tu_khoa:
            dieu_kien.append("(kh.hoten LIKE ? OR kh.makh LIKE ? OR p.tenphong LIKE ? OR p.maphong LIKE ?)")
            mau_tim = f"%{tu_khoa}%"
            tham_so.extend([mau_tim, mau_tim, mau_tim, mau_tim])

        menh_de_where = ("WHERE " + " AND ".join(dieu_kien)) if dieu_kien else ""

        with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
            cac_dong = ket_noi.execute(
                f"""
                SELECT
                    dp.id,
                    kh.makh || ' - ' || kh.hoten AS khachhang,
                    p.maphong || ' - ' || p.tenphong AS phong,
                    dp.ngay_nhan,
                    dp.ngay_tra,
                    dp.so_nguoi,
                    dp.gia_phong,
                    dp.trangthai,
                    hd.tong_tien
                FROM datphong dp
                JOIN khachhang kh ON kh.makh = dp.makh
                JOIN phong p ON p.maphong = dp.maphong
                LEFT JOIN hoa_don hd ON hd.datphong_id = dp.id
                {menh_de_where}
                ORDER BY dp.id DESC
                """,
                tham_so,
            ).fetchall()

        for chi_so, dong in enumerate(cac_dong):
            nhan_dong = "dong_chan" if chi_so % 2 == 0 else "dong_le"
            tong_tt = f"{dong['tong_tien']:,.0f} đ" if dong["tong_tien"] is not None else "—"
            doi_tuong.bang_du_lieu.insert(
                "",
                tk.END,
                values=(
                    dong["id"],
                    dong["khachhang"],
                    dong["phong"],
                    dong["ngay_nhan"],
                    dong["ngay_tra"],
                    f"{dong['so_nguoi']} người",
                    f"{dong['gia_phong']:,.0f} đ",
                    dong["trangthai"],
                    tong_tt,
                ),
                tags=(nhan_dong,),
            )

    def tao_dat_phong(doi_tuong):
        ma_kh = doi_tuong.ban_do_khach_hang.get(doi_tuong.hop_chon_khach.get())
        thong_tin_phong = doi_tuong.ban_do_phong.get(doi_tuong.hop_chon_phong.get())
        ngay_nhan_str = doi_tuong.o_ngay_nhan.get().strip()
        ngay_tra_str = doi_tuong.o_ngay_tra.get().strip()
        so_nguoi_str = doi_tuong.o_so_nguoi.get().strip()
        trang_thai_ban_dau = doi_tuong.hop_trang_thai_moi.get()

        if not ma_kh or not thong_tin_phong:
            messagebox.showwarning(
                "Thiếu thông tin",
                "Vui lòng chọn khách hàng và phòng.",
                parent=doi_tuong.cua_so_goc,
            )
            return

        ngay_nhan = _phan_tich_ngay_iso(ngay_nhan_str)
        ngay_tra = _phan_tich_ngay_iso(ngay_tra_str)
        if ngay_nhan is None or ngay_tra is None:
            messagebox.showwarning(
                "Sai định dạng ngày",
                "Ngày nhận và ngày trả phải đúng định dạng YYYY-MM-DD (ví dụ: 2026-11-16).",
                parent=doi_tuong.cua_so_goc,
            )
            return

        if ngay_tra <= ngay_nhan:
            messagebox.showwarning(
                "Ngày không hợp lệ",
                "Ngày trả phòng phải sau ngày nhận phòng ít nhất 1 đêm.",
                parent=doi_tuong.cua_so_goc,
            )
            return

        if not so_nguoi_str.isdigit() or int(so_nguoi_str) <= 0:
            messagebox.showwarning(
                "Số người không hợp lệ",
                "Số người ở phải là số nguyên lớn hơn 0.",
                parent=doi_tuong.cua_so_goc,
            )
            return

        ma_phong, gia_phong = thong_tin_phong
        ngay_dat_str = date.today().isoformat()

        try:
            with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
                ket_noi.execute(
                    """
                    INSERT INTO datphong (makh, maphong, ngay_dat, ngay_nhan, ngay_tra, so_nguoi, trangthai, gia_phong)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        ma_kh,
                        ma_phong,
                        ngay_dat_str,
                        ngay_nhan_str,
                        ngay_tra_str,
                        int(so_nguoi_str),
                        trang_thai_ban_dau,
                        gia_phong,
                    ),
                )
            messagebox.showinfo(
                "Thành công",
                f"Tạo phiếu đặt phòng {ma_phong} thành công!",
                parent=doi_tuong.cua_so_goc,
            )
            doi_tuong.tai_du_lieu_dat_phong()
        except sqlite3.IntegrityError as loi:
            messagebox.showerror(
                "Không thể đặt phòng",
                str(loi),
                parent=doi_tuong.cua_so_goc,
            )

    def _lay_luot_dat_dang_chon(doi_tuong):
        duoc_chon = doi_tuong.bang_du_lieu.selection()
        if not duoc_chon:
            messagebox.showwarning(
                "Chưa chọn phiếu",
                "Vui lòng chọn một lượt đặt phòng trong bảng danh sách.",
                parent=doi_tuong.cua_so_goc,
            )
            return None
        return doi_tuong.bang_du_lieu.item(duoc_chon[0], "values")

    def nhan_phong(doi_tuong):
        gia_tri = doi_tuong._lay_luot_dat_dang_chon()
        if not gia_tri:
            return
        dp_id, khach_hang, phong, _, _, _, _, trang_thai, _ = gia_tri
        if trang_thai != "Đã đặt":
            messagebox.showwarning(
                "Không thể nhận phòng",
                f"Chỉ có thể nhận phòng cho lượt ở trạng thái 'Đã đặt' (hiện tại: '{trang_thai}').",
                parent=doi_tuong.cua_so_goc,
            )
            return

        try:
            with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
                ket_noi.execute(
                    "UPDATE datphong SET trangthai = 'Đang ở' WHERE id = ?",
                    (dp_id,),
                )
            messagebox.showinfo(
                "Nhận phòng thành công",
                f"Khách {khach_hang} đã nhận {phong}.",
                parent=doi_tuong.cua_so_goc,
            )
            doi_tuong.tai_du_lieu_dat_phong()
        except sqlite3.IntegrityError as loi:
            messagebox.showerror("Lỗi", str(loi), parent=doi_tuong.cua_so_goc)

    def huy_dat_phong(doi_tuong):
        gia_tri = doi_tuong._lay_luot_dat_dang_chon()
        if not gia_tri:
            return
        dp_id, khach_hang, phong, _, _, _, _, trang_thai, _ = gia_tri
        if trang_thai != "Đã đặt":
            messagebox.showwarning(
                "Không thể hủy",
                f"Chỉ có thể hủy lượt đang ở trạng thái 'Đã đặt' (hiện tại: '{trang_thai}').",
                parent=doi_tuong.cua_so_goc,
            )
            return

        if messagebox.askyesno(
            "Xác nhận hủy",
            f"Bạn có chắc muốn hủy lượt đặt #{dp_id} ({phong} - {khach_hang})?",
            parent=doi_tuong.cua_so_goc,
        ):
            with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
                ket_noi.execute(
                    "UPDATE datphong SET trangthai = 'Đã hủy' WHERE id = ?",
                    (dp_id,),
                )
            messagebox.showinfo(
                "Đã hủy",
                "Đã hủy lượt đặt phòng.",
                parent=doi_tuong.cua_so_goc,
            )
            doi_tuong.tai_du_lieu_dat_phong()

    def mo_hop_thoai_thanh_toan(doi_tuong):
        gia_tri = doi_tuong._lay_luot_dat_dang_chon()
        if not gia_tri:
            return
        dp_id, khach_hang, phong, ngay_nhan_str, ngay_tra_str, _, gia_phong_str, trang_thai, _ = gia_tri
        if trang_thai != "Đang ở":
            messagebox.showwarning(
                "Không thể trả phòng",
                f"Chỉ lập hóa đơn & trả phòng cho lượt đang ở trạng thái 'Đang ở' (hiện tại: '{trang_thai}').",
                parent=doi_tuong.cua_so_goc,
            )
            return

        ngay_nhan = _phan_tich_ngay_iso(ngay_nhan_str)
        ngay_tra = _phan_tich_ngay_iso(ngay_tra_str)
        so_dem = max(1, (ngay_tra - ngay_nhan).days) if (ngay_nhan and ngay_tra) else 1
        don_gia = int(str(gia_phong_str).replace(",", "").replace(" đ", "").strip())
        tien_phong = so_dem * don_gia

        # Tự động lấy tổng tiền dịch vụ đã sử dụng của phiếu đặt phòng này
        tien_dich_vu, ds_tom_tat_dv = _lay_chi_tiet_dich_vu_theo_dat_phong(
            doi_tuong.duong_dan_co_so_du_lieu, dp_id
        )
        tien_dich_vu_int = int(round(tien_dich_vu))

        hop_thoai = tk.Toplevel(doi_tuong.cua_so_goc)
        hop_thoai.title(f"Lập hóa đơn & Trả phòng - Mã ĐP #{dp_id}")
        hop_thoai.geometry("470x510")
        hop_thoai.configure(bg=doi_tuong.the_nen)
        hop_thoai.transient(doi_tuong.cua_so_goc)
        hop_thoai.grab_set()

        khung = tk.Frame(hop_thoai, bg=doi_tuong.the_nen, padx=24, pady=20)
        khung.pack(fill="both", expand=True)

        tk.Label(
            khung,
            text="HÓA ĐƠN THANH TOÁN TRẢ PHÒNG",
            font=("Arial", 13, "bold"),
            fg=doi_tuong.dieu_huong_nen,
            bg=doi_tuong.the_nen,
        ).pack(anchor="w", pady=(0, 10))

        chi_tiet_dv_txt = (
            "\n".join(ds_tom_tat_dv) if ds_tom_tat_dv else "• Không sử dụng dịch vụ thêm"
        )
        thong_tin_chi_tiet = (
            f"Khách hàng: {khach_hang}\n"
            f"Phòng lưu trú: {phong}\n"
            f"Thời gian: {ngay_nhan_str} → {ngay_tra_str} ({so_dem} đêm)\n"
            f"Tiền phòng ({don_gia:,.0f} đ × {so_dem} đêm): {tien_phong:,.0f} đ\n"
            f"Tiền dịch vụ đã sử dụng: {tien_dich_vu_int:,.0f} đ\n"
            f"{chi_tiet_dv_txt}"
        )
        tk.Label(
            khung,
            text=thong_tin_chi_tiet,
            font=("Arial", 9),
            fg=doi_tuong.van_ban_mau,
            bg="#F4F6F9",
            justify="left",
            padx=12,
            pady=10,
        ).pack(fill="x", pady=(0, 12))

        tk.Label(
            khung,
            text="Phụ phí phát sinh khác (VNĐ)",
            font=("Arial", 9, "bold"),
            fg=doi_tuong.phu_mau,
            bg=doi_tuong.the_nen,
        ).pack(anchor="w")
        o_phu_phi = ONhapLieuKhachSan(khung)
        o_phu_phi.insert(0, "0")
        o_phu_phi.pack(fill="x", pady=(2, 10))

        tk.Label(
            khung,
            text="Phương thức thanh toán",
            font=("Arial", 9, "bold"),
            fg=doi_tuong.phu_mau,
            bg=doi_tuong.the_nen,
        ).pack(anchor="w")
        hop_phuong_thuc = OHopChonKhachSan(
            khung, values=("Tiền mặt", "Chuyển khoản", "Thẻ")
        )
        hop_phuong_thuc.set("Tiền mặt")
        hop_phuong_thuc.pack(fill="x", pady=(2, 12))

        tong_mac_dinh = tien_phong + tien_dich_vu_int
        nhan_tong = tk.Label(
            khung,
            text=f"TỔNG THANH TOÁN: {tong_mac_dinh:,.0f} đ",
            font=("Arial", 12, "bold"),
            fg=doi_tuong.nhan_manh_mau,
            bg=doi_tuong.the_nen,
        )
        nhan_tong.pack(anchor="w", pady=(0, 14))

        def cap_nhat_tong(event=None):
            chuoi = o_phu_phi.get().strip().replace(",", "")
            phu_phi_khac = int(chuoi) if chuoi.isdigit() else 0
            nhan_tong.config(
                text=f"TỔNG THANH TOÁN: {tien_phong + tien_dich_vu_int + phu_phi_khac:,.0f} đ"
            )

        o_phu_phi.bind("<KeyRelease>", cap_nhat_tong)

        def xac_nhan_thanh_toan():
            chuoi = o_phu_phi.get().strip().replace(",", "")
            if not chuoi.isdigit():
                messagebox.showwarning(
                    "Phụ phí không hợp lệ",
                    "Phụ phí phải là số nguyên không âm.",
                    parent=hop_thoai,
                )
                return

            phu_phi_khac = int(chuoi)
            tong_phu_phi = tien_dich_vu_int + phu_phi_khac
            tong_tien = tien_phong + tong_phu_phi
            phuong_thuc = hop_phuong_thuc.get()
            ngay_tt = date.today().isoformat()

            try:
                with mo_ket_noi_co_so_du_lieu(doi_tuong.duong_dan_co_so_du_lieu) as ket_noi:
                    ket_noi.execute(
                        """
                        INSERT INTO hoa_don (datphong_id, ngay_thanh_toan, so_dem, tien_phong, phu_phi, tong_tien, phuong_thuc)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (dp_id, ngay_tt, so_dem, tien_phong, tong_phu_phi, tong_tien, phuong_thuc),
                    )
                    ket_noi.execute(
                        "UPDATE datphong SET trangthai = 'Đã trả' WHERE id = ?",
                        (dp_id,),
                    )
                hop_thoai.destroy()
                messagebox.showinfo(
                    "Hoàn tất trả phòng",
                    f"Đã lập hóa đơn ({tong_tien:,.0f} đ — gồm {tien_dich_vu_int:,.0f} đ tiền dịch vụ) và hoàn tất trả phòng!",
                    parent=doi_tuong.cua_so_goc,
                )
                doi_tuong.tai_du_lieu_dat_phong()
            except sqlite3.IntegrityError as loi:
                messagebox.showerror("Lỗi dữ liệu", str(loi), parent=hop_thoai)

        khung_nut = tk.Frame(khung, bg=doi_tuong.the_nen)
        khung_nut.pack(fill="x")
        tao_nut_khach_san(
            khung_nut,
            "XÁC NHẬN THANH TOÁN",
            xac_nhan_thanh_toan,
            doi_tuong.dieu_huong_nen,
            padx=14,
        ).pack(side="left", padx=(0, 8))
        tao_nut_khach_san(
            khung_nut,
            "Hủy",
            hop_thoai.destroy,
            "#64748B",
            padx=14,
        ).pack(side="left")


if __name__ == "__main__":
    cua_so = tk.Tk()
    cua_so.title("Quản lý đặt phòng & Hóa đơn - THANHVY Hotel")
    cua_so.geometry("1080x680")
    cua_so.configure(bg=BANG_MAU_KHACH_SAN["nen_chinh"])
    cau_hinh_giao_dien_ttk(cua_so)

    class UngDungGiaLap:
        cua_so_goc = cua_so
        duong_dan_co_so_du_lieu = "QLKS.db"

    khung = tk.Frame(cua_so, bg=BANG_MAU_KHACH_SAN["nen_chinh"], padx=16, pady=16)
    khung.pack(fill="both", expand=True)
    BieuMauDatPhong(UngDungGiaLap(), khung).tao_giao_dien()
    cua_so.mainloop()