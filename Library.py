def can_giua_cua_so(cua_so, chieu_rong=850, chieu_cao=600):
    chieu_rong_man_hinh = cua_so.winfo_screenwidth()
    chieu_cao_man_hinh = cua_so.winfo_screenheight()
    toa_do_x = (chieu_rong_man_hinh // 2) - (chieu_rong // 2)
    toa_do_y = (chieu_cao_man_hinh // 2) - (chieu_cao // 2)
    cua_so.geometry(f'{chieu_rong}x{chieu_cao}+{toa_do_x}+{toa_do_y}')