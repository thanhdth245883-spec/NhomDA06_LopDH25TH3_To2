from pathlib import Path
import hashlib
import os
import sqlite3
import unicodedata


def mo_ket_noi_co_so_du_lieu(duong_dan):
    ket_noi = sqlite3.connect(duong_dan)
    ket_noi.row_factory = sqlite3.Row
    ket_noi.execute("PRAGMA foreign_keys = ON")
    return ket_noi


def bam_mat_khau(mat_khau: str) -> str:
    muoi = os.urandom(16)
    ban_bam = hashlib.pbkdf2_hmac("sha256", mat_khau.encode("utf-8"), muoi, 100_000)
    return f"pbkdf2_sha256$100000${muoi.hex()}${ban_bam.hex()}"


def _tao_cau_truc_co_so_du_lieu(ket_noi):
    cac_bang = (
        """
        CREATE TABLE IF NOT EXISTS nhanvien (
            manv TEXT PRIMARY KEY NOT NULL CHECK (length(trim(manv)) > 0),
            hoten TEXT NOT NULL CHECK (length(trim(hoten)) > 0),
            tendangnhap TEXT NOT NULL COLLATE NOCASE UNIQUE
                CHECK (length(trim(tendangnhap)) > 0),
            sodt TEXT,
            chucvu TEXT NOT NULL CHECK (chucvu IN ('Quản lý', 'Nhân viên')),
            matkhau_hash TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS khachhang (
            makh TEXT PRIMARY KEY NOT NULL CHECK (length(trim(makh)) > 0),
            hoten TEXT NOT NULL CHECK (length(trim(hoten)) > 0),
            cccd TEXT NOT NULL CHECK (length(trim(cccd)) > 0),
            sodt TEXT,
            gioitinh TEXT CHECK (gioitinh IS NULL OR gioitinh IN ('Nam', 'Nữ'))
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS loaiphong (
            maloai TEXT PRIMARY KEY NOT NULL,
            tenloai TEXT NOT NULL CHECK (length(trim(tenloai)) > 0),
            tenloai_key TEXT NOT NULL UNIQUE,
            giaphong INTEGER NOT NULL CHECK (giaphong >= 0 AND giaphong = CAST(giaphong AS INTEGER))
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS phong (
            maphong TEXT PRIMARY KEY NOT NULL CHECK (length(trim(maphong)) > 0),
            tenphong TEXT NOT NULL CHECK (length(trim(tenphong)) > 0),
            maloai TEXT NOT NULL REFERENCES loaiphong(maloai) ON UPDATE CASCADE ON DELETE RESTRICT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS datphong (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            makh TEXT NOT NULL REFERENCES khachhang(makh) ON DELETE RESTRICT,
            maphong TEXT NOT NULL REFERENCES phong(maphong) ON DELETE RESTRICT,
            ngay_dat TEXT NOT NULL CHECK (date(ngay_dat) IS NOT NULL AND date(ngay_dat) = ngay_dat),
            ngay_nhan TEXT NOT NULL CHECK (date(ngay_nhan) IS NOT NULL AND date(ngay_nhan) = ngay_nhan),
            ngay_tra TEXT NOT NULL CHECK (date(ngay_tra) IS NOT NULL AND date(ngay_tra) = ngay_tra),
            so_nguoi INTEGER NOT NULL CHECK (so_nguoi > 0),
            trangthai TEXT NOT NULL DEFAULT 'Đã đặt' CHECK (trangthai IN ('Đã đặt', 'Đang ở', 'Đã trả', 'Đã hủy')),
            gia_phong INTEGER NOT NULL CHECK (gia_phong >= 0 AND gia_phong = CAST(gia_phong AS INTEGER)),
            CHECK (ngay_tra > ngay_nhan)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS hoa_don (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datphong_id INTEGER NOT NULL UNIQUE REFERENCES datphong(id) ON DELETE RESTRICT,
            ngay_thanh_toan TEXT NOT NULL CHECK (date(ngay_thanh_toan) IS NOT NULL AND date(ngay_thanh_toan) = ngay_thanh_toan),
            so_dem INTEGER NOT NULL CHECK (so_dem > 0),
            tien_phong INTEGER NOT NULL CHECK (tien_phong >= 0 AND tien_phong = CAST(tien_phong AS INTEGER)),
            phu_phi INTEGER NOT NULL DEFAULT 0 CHECK (phu_phi >= 0 AND phu_phi = CAST(phu_phi AS INTEGER)),
            tong_tien INTEGER NOT NULL CHECK (tong_tien >= 0 AND tong_tien = CAST(tong_tien AS INTEGER) AND tong_tien = tien_phong + phu_phi),
            phuong_thuc TEXT NOT NULL CHECK (phuong_thuc IN ('Tiền mặt', 'Chuyển khoản', 'Thẻ'))
        )
        """,
    )
    for cau_lenh_sql in cac_bang:
        ket_noi.execute(cau_lenh_sql)

    cac_chi_muc = (
        "CREATE INDEX IF NOT EXISTS idx_phong_maloai ON phong(maloai)",
        "CREATE INDEX IF NOT EXISTS idx_datphong_room_dates ON datphong(maphong, ngay_nhan, ngay_tra, trangthai)",
        "CREATE INDEX IF NOT EXISTS idx_datphong_guest_dates ON datphong(makh, ngay_nhan, ngay_tra)",
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_khachhang_cccd_unique ON khachhang(LOWER(TRIM(cccd)))",
        "CREATE INDEX IF NOT EXISTS idx_khachhang_hoten ON khachhang(hoten)",
    )
    for cau_lenh_sql in cac_chi_muc:
        ket_noi.execute(cau_lenh_sql)

    cac_kich_hoat = (
        """
        CREATE TRIGGER IF NOT EXISTS prevent_booking_overlap_insert
        BEFORE INSERT ON datphong
        WHEN NEW.trangthai IN ('Đã đặt', 'Đang ở')
        BEGIN
            SELECT RAISE(ABORT, 'Phòng đã có lượt đặt trùng ngày.')
            WHERE EXISTS (
                SELECT 1 FROM datphong existing
                WHERE existing.maphong = NEW.maphong
                  AND existing.trangthai IN ('Đã đặt', 'Đang ở')
                  AND existing.ngay_nhan < NEW.ngay_tra
                  AND existing.ngay_tra > NEW.ngay_nhan
            );
        END
        """,
        """
        CREATE TRIGGER IF NOT EXISTS prevent_booking_overlap_update
        BEFORE UPDATE OF maphong, ngay_nhan, ngay_tra, trangthai ON datphong
        WHEN NEW.trangthai IN ('Đã đặt', 'Đang ở')
        BEGIN
            SELECT RAISE(ABORT, 'Phòng đã có lượt đặt trùng ngày.')
            WHERE EXISTS (
                SELECT 1 FROM datphong existing
                WHERE existing.id != NEW.id
                  AND existing.maphong = NEW.maphong
                  AND existing.trangthai IN ('Đã đặt', 'Đang ở')
                  AND existing.ngay_nhan < NEW.ngay_tra
                  AND existing.ngay_tra > NEW.ngay_nhan
            );
        END
        """,
        """
        CREATE TRIGGER IF NOT EXISTS validate_booking_status_transition
        BEFORE UPDATE OF trangthai ON datphong
        WHEN OLD.trangthai != NEW.trangthai
         AND NOT (
            (OLD.trangthai = 'Đã đặt' AND NEW.trangthai IN ('Đang ở', 'Đã hủy'))
            OR (OLD.trangthai = 'Đang ở' AND NEW.trangthai = 'Đã trả')
         )
        BEGIN
            SELECT RAISE(ABORT, 'Chuyển trạng thái lượt đặt không hợp lệ.');
        END
        """,
        """
        CREATE TRIGGER IF NOT EXISTS require_invoice_before_checkout
        BEFORE UPDATE OF trangthai ON datphong
        WHEN NEW.trangthai = 'Đã trả'
         AND NOT EXISTS (
            SELECT 1 FROM hoa_don WHERE datphong_id = NEW.id
         )
        BEGIN
            SELECT RAISE(ABORT, 'Cần tạo hóa đơn trước khi hoàn tất trả phòng.');
        END
        """,
        """
        CREATE TRIGGER IF NOT EXISTS invoice_requires_active_stay
        BEFORE INSERT ON hoa_don
        WHEN NOT EXISTS (
            SELECT 1 FROM datphong
            WHERE id = NEW.datphong_id AND trangthai = 'Đang ở'
        )
        BEGIN
            SELECT RAISE(ABORT, 'Chỉ được lập hóa đơn cho lượt đang lưu trú.');
        END
        """,
    )
    for cau_lenh_sql in cac_kich_hoat:
        ket_noi.execute(cau_lenh_sql)


def _tao_du_lieu_mau(con_tro_du_lieu):
    if not con_tro_du_lieu.execute("SELECT 1 FROM nhanvien LIMIT 1").fetchone():
        danh_sach_nhan_vien = (
            ("NV001", "Nguyễn Thúy Hà", "admin", "0903000001", "Quản lý", "123456"),
            ("NV002", "Bùi Thanh Sang", "nhanvien1", "0903000002", "Nhân viên", "Nhanvien123!"),
            ("NV003", "Võ Thị Ngọc Hân", "nhanvien2", "0903000003", "Nhân viên", "Nhanvien123!"),
        )
        con_tro_du_lieu.executemany(
            """
            INSERT INTO nhanvien (manv, hoten, tendangnhap, sodt, chucvu, matkhau_hash)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (ma_nhan_vien, ten, ten_dang_nhap, so_dien_thoai, chuc_vu, bam_mat_khau(mat_khau))
                for ma_nhan_vien, ten, ten_dang_nhap, so_dien_thoai, chuc_vu, mat_khau in danh_sach_nhan_vien
            ],
        )

    con_tro_du_lieu.executemany(
        "INSERT OR IGNORE INTO loaiphong (maloai, tenloai, tenloai_key, giaphong) VALUES (?, ?, ?, ?)",
        [
            ("LP01", "Phòng Đơn Tiêu Chuẩn", khoa_loai_phong("Phòng Đơn Tiêu Chuẩn"), 350000),
            ("LP02", "Phòng Deluxe", khoa_loai_phong("Phòng Deluxe"), 850000),
            ("LP03", "Phòng Gia Đình", khoa_loai_phong("Phòng Gia Đình"), 1200000),
            ("LP04", "Phòng Suite Hoàng Gia", khoa_loai_phong("Phòng Suite Hoàng Gia"), 2000000),
        ],
    )

    con_tro_du_lieu.executemany(
        "INSERT OR IGNORE INTO phong (maphong, tenphong, maloai) VALUES (?, ?, ?)",
        [
            ("P101", "Phòng 101", "LP01"),
            ("P102", "Phòng 102", "LP01"),
            ("P103", "Phòng 103", "LP01"),
            ("P104", "Phòng 104", "LP01"),
            ("P201", "Phòng 201", "LP02"),
            ("P202", "Phòng 202", "LP02"),
            ("P203", "Phòng 203", "LP02"),
            ("P204", "Phòng 204", "LP02"),
            ("P301", "Phòng 301", "LP03"),
            ("P302", "Phòng 302", "LP03"),
            ("P303", "Phòng 303", "LP03"),
            ("P401", "Phòng 401 (VIP Suite)", "LP04"),
        ],
    )

    con_tro_du_lieu.executemany(
        "INSERT OR IGNORE INTO khachhang (makh, hoten, cccd, sodt, gioitinh) VALUES (?, ?, ?, ?, ?)",
        [
            ("KH001", "Nguyễn Hoàng Nam", "0902000101", "0902000101", "Nam"),
            ("KH002", "Trần Thu Hà", "0902000102", "0902000102", "Nữ"),
            ("KH003", "Lê Minh Khang", "0902000103", "0902000103", "Nam"),
            ("KH004", "Đặng Nguyễn Thiên Thanh", "0902000104", "0902000104", "Nữ"),
            ("KH005", "Nguyễn Thị Thúy Vy", "0902000105", "0902000105", "Nữ"),
            ("KH006", "Phạm Thanh Thảo", "0902000106", "0902000106", "Nữ"),
            ("KH007", "Vũ Hoàng Long", "0902000107", "0902000107", "Nam"),
            ("KH008", "Đỗ Mai Phương", "0902000108", "0902000108", "Nữ"),
            ("KH009", "Trương Gia Bảo", "0902000109", "0902000109", "Nam"),
            ("KH010", "Bùi Ngọc Ánh", "0902000110", "0902000110", "Nữ"),
            ("KH011", "Hoàng Quốc Tuấn", "0902000111", "0902000111", "Nam"),
            ("KH012", "Ngô Mỹ Duyên", "0902000112", "0902000112", "Nữ"),
            ("KH013", "Đinh Văn Hậu", "0902000113", "0902000113", "Nam"),
            ("KH014", "Phan Thị Yến", "0902000114", "0902000114", "Nữ"),
            ("KH015", "Dương Kiến Văn", "0902000115", "0902000115", "Nam"),
        ],
    )

    if not con_tro_du_lieu.execute("SELECT 1 FROM datphong LIMIT 1").fetchone():
        cac_da_tra = [
            ("KH001", "P101", "2026-11-01", "2026-11-01", "2026-11-03", 2, 350000, 2, 50000, "Tiền mặt", "2026-11-03"),
            ("KH003", "P102", "2026-11-01", "2026-11-02", "2026-11-04", 1, 350000, 2, 0, "Chuyển khoản", "2026-11-04"),
            ("KH004", "P202", "2026-11-02", "2026-11-03", "2026-11-06", 2, 850000, 3, 100000, "Thẻ", "2026-11-06"),
            ("KH005", "P301", "2026-11-03", "2026-11-04", "2026-11-07", 3, 1200000, 3, 0, "Tiền mặt", "2026-11-07"),
            ("KH006", "P103", "2026-11-04", "2026-11-05", "2026-11-07", 1, 350000, 2, 0, "Tiền mặt", "2026-11-07"),
            ("KH007", "P401", "2026-11-05", "2026-11-06", "2026-11-09", 2, 2000000, 3, 300000, "Chuyển khoản", "2026-11-09"),
            ("KH008", "P203", "2026-11-06", "2026-11-07", "2026-11-09", 2, 850000, 2, 50000, "Thẻ", "2026-11-09"),
            ("KH009", "P104", "2026-11-07", "2026-11-08", "2026-11-10", 1, 350000, 2, 0, "Tiền mặt", "2026-11-10"),
            ("KH010", "P302", "2026-11-08", "2026-11-09", "2026-11-12", 4, 1200000, 3, 200000, "Chuyển khoản", "2026-11-12"),
            ("KH011", "P204", "2026-11-09", "2026-11-10", "2026-11-13", 2, 850000, 3, 100000, "Thẻ", "2026-11-13"),
            ("KH012", "P101", "2026-11-10", "2026-11-11", "2026-11-14", 1, 350000, 3, 0, "Tiền mặt", "2026-11-14"),
            ("KH013", "P303", "2026-11-11", "2026-11-12", "2026-11-15", 3, 1200000, 3, 150000, "Chuyển khoản", "2026-11-15"),
        ]

        for makh, maphong, ngay_dat, ngay_nhan, ngay_tra, so_nguoi, gia_phong, so_dem, phu_phi, phuong_thuc, ngay_tt in cac_da_tra:
            con_tro_du_lieu.execute(
                """
                INSERT INTO datphong (makh, maphong, ngay_dat, ngay_nhan, ngay_tra, so_nguoi, trangthai, gia_phong)
                VALUES (?, ?, ?, ?, ?, ?, 'Đang ở', ?)
                """,
                (makh, maphong, ngay_dat, ngay_nhan, ngay_tra, so_nguoi, gia_phong),
            )
            dp_id = con_tro_du_lieu.lastrowid
            tien_phong = so_dem * gia_phong
            tong_tien = tien_phong + phu_phi
            con_tro_du_lieu.execute(
                """
                INSERT INTO hoa_don (datphong_id, ngay_thanh_toan, so_dem, tien_phong, phu_phi, tong_tien, phuong_thuc)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (dp_id, ngay_tt, so_dem, tien_phong, phu_phi, tong_tien, phuong_thuc),
            )
            con_tro_du_lieu.execute(
                "UPDATE datphong SET trangthai = 'Đã trả' WHERE id = ?",
                (dp_id,),
            )

        # Lượt lưu trú hiện tại
        con_tro_du_lieu.execute(
            """
            INSERT INTO datphong (makh, maphong, ngay_dat, ngay_nhan, ngay_tra, so_nguoi, trangthai, gia_phong)
            VALUES ('KH002', 'P201', '2026-11-08', '2026-11-13', '2026-11-18', 2, 'Đang ở', 850000)
            """
        )
        con_tro_du_lieu.execute(
            """
            INSERT INTO datphong (makh, maphong, ngay_dat, ngay_nhan, ngay_tra, so_nguoi, trangthai, gia_phong)
            VALUES ('KH014', 'P301', '2026-11-14', '2026-11-14', '2026-11-17', 2, 'Đang ở', 1200000)
            """
        )

        # Lượt đặt trước
        con_tro_du_lieu.execute(
            """
            INSERT INTO datphong (makh, maphong, ngay_dat, ngay_nhan, ngay_tra, so_nguoi, trangthai, gia_phong)
            VALUES ('KH015', 'P102', '2026-11-14', '2026-11-16', '2026-11-19', 1, 'Đã đặt', 350000)
            """
        )
        con_tro_du_lieu.execute(
            """
            INSERT INTO datphong (makh, maphong, ngay_dat, ngay_nhan, ngay_tra, so_nguoi, trangthai, gia_phong)
            VALUES ('KH001', 'P401', '2026-11-15', '2026-11-18', '2026-11-21', 2, 'Đã đặt', 2000000)
            """
        )

        # Lượt đã hủy
        con_tro_du_lieu.execute(
            """
            INSERT INTO datphong (makh, maphong, ngay_dat, ngay_nhan, ngay_tra, so_nguoi, trangthai, gia_phong)
            VALUES ('KH003', 'P103', '2026-11-13', '2026-11-20', '2026-11-23', 1, 'Đã đặt', 350000)
            """
        )
        huy_id = con_tro_du_lieu.lastrowid
        con_tro_du_lieu.execute(
            "UPDATE datphong SET trangthai = 'Đã hủy' WHERE id = ?",
            (huy_id,),
        )


def khoa_loai_phong(ten):
    da_chuan_hoa = unicodedata.normalize("NFKC", ten)
    return " ".join(da_chuan_hoa.split()).casefold()


def khoi_tao_co_so_du_lieu(duong_dan_co_so_du_lieu=None, thong_bao=True):
    duong_dan = Path(duong_dan_co_so_du_lieu) if duong_dan_co_so_du_lieu else Path(__file__).with_name("QLKS.db")
    with mo_ket_noi_co_so_du_lieu(duong_dan) as ket_noi:
        _tao_cau_truc_co_so_du_lieu(ket_noi)
        _tao_du_lieu_mau(ket_noi.cursor())
        ket_noi.execute("PRAGMA user_version = 3")
    if thong_bao:
        print(f"Khởi tạo cơ sở dữ liệu SQLite {duong_dan} thành công!")


if __name__ == "__main__":
    khoi_tao_co_so_du_lieu()