import hashlib
from db_connection import mo_ket_noi_co_so_du_lieu


def _bam_mat_khau(mat_khau):
    return hashlib.sha256(mat_khau.encode("utf-8")).hexdigest()


def _lay_ten_cot_nhan_vien(ket_noi):
    cac_cot = [
        dong[1] for dong in ket_noi.execute("PRAGMA table_info(nhanvien)").fetchall()
    ]
    cot_mk = next(
        (
            c
            for c in cac_cot
            if c.lower() in ("matkhau", "mat_khau", "password", "matkhaubam", "mat_khau_bam")
        ),
        "matkhau",
    )
    cot_cv = next(
        (c for c in cac_cot if c.lower() in ("chucvu", "chuc_vu", "vaitro", "role")),
        "chucvu",
    )
    return cot_mk, cot_cv


def xac_thuc_dang_nhap(ten_dang_nhap, mat_khau, duong_dan_db=None):
    ten_sach = (ten_dang_nhap or "").strip()
    mk_sach = (mat_khau or "").strip()
    if not ten_sach or not mk_sach:
        return None

    with mo_ket_noi_co_so_du_lieu(duong_dan_db) as ket_noi:
        cot_mk, cot_cv = _lay_ten_cot_nhan_vien(ket_noi)
        dong = ket_noi.execute(
            f"""
            SELECT manv, hoten, tendangnhap, {cot_mk} AS matkhau, {cot_cv} AS chucvu
            FROM nhanvien
            WHERE tendangnhap = ?
            """,
            (ten_sach,),
        ).fetchone()

    if dong is None:
        return None

    mk_luu = dong["matkhau"]
    if mk_luu in (mk_sach, _bam_mat_khau(mk_sach)):
        return {
            "manv": dong["manv"],
            "hoten": dong["hoten"],
            "tendangnhap": dong["tendangnhap"],
            "chucvu": dong["chucvu"] or "Nhân viên",
        }
    return None


xac_thuc_tai_khoan = lambda duong_dan_db, ten_dang_nhap, mat_khau: xac_thuc_dang_nhap(
    ten_dang_nhap, mat_khau, duong_dan_db
)