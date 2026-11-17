from contextlib import contextmanager
from pathlib import Path
import sqlite3

DUONG_DAN_MAC_DINH = Path(__file__).with_name("QLKS.db")


@contextmanager
def mo_ket_noi_co_so_du_lieu(duong_dan_co_so_du_lieu=None):
    duong_dan = (
        Path(duong_dan_co_so_du_lieu)
        if duong_dan_co_so_du_lieu
        else DUONG_DAN_MAC_DINH
    )
    ket_noi = sqlite3.connect(str(duong_dan))
    ket_noi.row_factory = sqlite3.Row
    ket_noi.execute("PRAGMA foreign_keys = ON")
    try:
        yield ket_noi
        ket_noi.commit()
    except Exception:
        ket_noi.rollback()
        raise
    finally:
        ket_noi.close()