import tkinter as tk
from tkinter import ttk


# Bảng màu chủ đạo mới: Xanh Navy Hoàng Gia & Vàng Đồng Ấm
BANG_MAU_KHACH_SAN = {
    "nen_chinh": "#F4F6F9",        # Xám xanh nhạt dịu mắt
    "dieu_huong_nen": "#1B2A4A",   # Xanh Navy đậm sang trọng
    "nhan_manh_mau": "#C59B27",    # Vàng đồng hoàng gia
    "van_ban_mau": "#1E293B",      # Xám than đậm
    "phu_mau": "#64748B",          # Xám xanh trung tính
    "the_nen": "#FFFFFF",          # Nền thẻ trắng tinh
    "vien_the": "#CBD5E1",         # Viền thẻ xám nhạt
    "dong_chan": "#F8FAFC",        # Màu dòng xen kẽ Treeview
    "chon_dong": "#DBEAFE",        # Màu dòng đang chọn
}


def _lam_sang_mau(ma_mau, he_so=0.18):
    """Tự động tính màu sáng hơn khi rê chuột vào nút."""
    ma_mau = ma_mau.lstrip("#")
    if len(ma_mau) != 6:
        return f"#{ma_mau}"
    r = min(255, int(int(ma_mau[0:2], 16) + (255 - int(ma_mau[0:2], 16)) * he_so))
    g = min(255, int(int(ma_mau[2:4], 16) + (255 - int(ma_mau[2:4], 16)) * he_so))
    b = min(255, int(int(ma_mau[4:6], 16) + (255 - int(ma_mau[4:6], 16)) * he_so))
    return f"#{r:02X}{g:02X}{b:02X}"


def cau_hinh_giao_dien_ttk(cua_so_goc):
    """Khởi tạo style đồng bộ cho Treeview, Entry, Combobox và Scrollbar."""
    kieu = ttk.Style(cua_so_goc)
    if "clam" in kieu.theme_names():
        kieu.theme_use("clam")

    # Style bảng dữ liệu (Treeview)
    kieu.configure(
        "Hotel.Treeview",
        background=BANG_MAU_KHACH_SAN["the_nen"],
        foreground=BANG_MAU_KHACH_SAN["van_ban_mau"],
        fieldbackground=BANG_MAU_KHACH_SAN["the_nen"],
        rowheight=32,
        font=("Arial", 10),
        borderwidth=1,
        relief="solid",
    )
    kieu.configure(
        "Hotel.Treeview.Heading",
        background=BANG_MAU_KHACH_SAN["dieu_huong_nen"],
        foreground="#FFFFFF",
        font=("Arial", 10, "bold"),
        relief="flat",
        padding=(8, 8),
    )
    kieu.map(
        "Hotel.Treeview.Heading",
        background=[("active", "#2B4170")],
    )
    kieu.map(
        "Hotel.Treeview",
        background=[("selected", BANG_MAU_KHACH_SAN["chon_dong"])],
        foreground=[("selected", BANG_MAU_KHACH_SAN["dieu_huong_nen"])],
    )

    # Style ô nhập liệu (Entry & Combobox)
    kieu.configure(
        "Hotel.TEntry",
        fieldbackground="#FFFFFF",
        foreground=BANG_MAU_KHACH_SAN["van_ban_mau"],
        bordercolor=BANG_MAU_KHACH_SAN["vien_the"],
        lightcolor=BANG_MAU_KHACH_SAN["nhan_manh_mau"],
        darkcolor=BANG_MAU_KHACH_SAN["vien_the"],
        padding=(8, 6),
        font=("Arial", 10),
    )
    kieu.configure(
        "Hotel.TCombobox",
        fieldbackground="#FFFFFF",
        background="#E2E8F0",
        foreground=BANG_MAU_KHACH_SAN["van_ban_mau"],
        bordercolor=BANG_MAU_KHACH_SAN["vien_the"],
        padding=(8, 6),
        font=("Arial", 10),
    )

    # Style thanh cuộn dọc
    kieu.configure(
        "Hotel.Vertical.TScrollbar",
        background="#CBD5E1",
        troughcolor=BANG_MAU_KHACH_SAN["nen_chinh"],
        bordercolor=BANG_MAU_KHACH_SAN["nen_chinh"],
        arrowcolor=BANG_MAU_KHACH_SAN["dieu_huong_nen"],
    )


def tao_bang_du_lieu(
    khung_cha,
    cac_cot,
    tieu_de_cac_cot,
    do_rong_cac_cot,
    can_le_cac_cot=None,
    dem_ngang=0,
    dem_doc=0,
    mau_nen="#FFFFFF",
):
    khung = tk.Frame(khung_cha, bg=mau_nen)
    khung.pack(fill="both", expand=True, padx=dem_ngang, pady=dem_doc)

    bang = ttk.Treeview(
        khung,
        columns=cac_cot,
        show="headings",
        style="Hotel.Treeview",
        selectmode="browse",
    )
    thanh_cuon = ttk.Scrollbar(
        khung,
        orient="vertical",
        command=bang.yview,
        style="Hotel.Vertical.TScrollbar",
    )
    bang.configure(yscrollcommand=thanh_cuon.set)

    # Cấu hình màu dòng xen kẽ (zebra striping) cho bảng dễ đọc
    bang.tag_configure("dong_le", background=BANG_MAU_KHACH_SAN["the_nen"])
    bang.tag_configure("dong_chan", background=BANG_MAU_KHACH_SAN["dong_chan"])

    can_le_cac_cot = can_le_cac_cot or ("center",) * len(cac_cot)
    for cot, tieu_de, do_rong, can_le in zip(
        cac_cot, tieu_de_cac_cot, do_rong_cac_cot, can_le_cac_cot
    ):
        bang.heading(cot, text=tieu_de)
        bang.column(cot, width=do_rong, anchor=can_le)

    bang.pack(side="left", fill="both", expand=True)
    thanh_cuon.pack(side="right", fill="y")
    return bang


def xoa_du_lieu_bang(bang):
    for ma_dong in bang.get_children():
        bang.delete(ma_dong)


class ONhapLieuKhachSan(ttk.Entry):
    def __init__(doi_tuong, khung_cha=None, **cac_tham_so_tu_khoa):
        cac_tham_so_tu_khoa.setdefault("cursor", "xterm")
        cac_tham_so_tu_khoa.setdefault("style", "Hotel.TEntry")
        super().__init__(khung_cha, **cac_tham_so_tu_khoa)


class OHopChonKhachSan(ttk.Combobox):
    def __init__(doi_tuong, khung_cha=None, **cac_tham_so_tu_khoa):
        cac_tham_so_tu_khoa.setdefault("cursor", "hand2")
        cac_tham_so_tu_khoa.setdefault("style", "Hotel.TCombobox")
        cac_tham_so_tu_khoa.setdefault("state", "readonly")
        super().__init__(khung_cha, **cac_tham_so_tu_khoa)


def tao_nut_khach_san(khung_cha, van_ban, lenh, mau="#1B2A4A", padx=14):
    mau_di_chuot = _lam_sang_mau(mau, 0.16)
    nut = tk.Frame(
        khung_cha,
        bg=mau,
        highlightthickness=1,
        highlightbackground=mau,
        cursor="hand2",
    )
    nhan = tk.Label(
        nut,
        text=van_ban,
        bg=mau,
        fg="#FFFFFF",
        font=("Arial", 10, "bold"),
        padx=padx,
        pady=9,
        cursor="hand2",
        takefocus=True,
    )
    nhan.pack()

    def dat_mau(mau_moi):
        nut.config(bg=mau_moi, highlightbackground=mau_moi)
        nhan.config(bg=mau_moi)

    for thanh_phan_giao_dien in (nut, nhan):
        thanh_phan_giao_dien.bind("<Button-1>", lambda _: lenh())
        thanh_phan_giao_dien.bind("<Enter>", lambda _: dat_mau(mau_di_chuot))
        thanh_phan_giao_dien.bind("<Leave>", lambda _: dat_mau(mau))
    return nut