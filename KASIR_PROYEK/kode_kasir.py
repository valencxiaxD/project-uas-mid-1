import sys
import csv
import os
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, 
                             QGridLayout, QTableWidget, QTableWidgetItem, QComboBox, 
                             QMessageBox, QStackedWidget, QHBoxLayout, QVBoxLayout,
                             QHeaderView, QFrame)
from PyQt5.QtCore import Qt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.csv")
TRANSAKSI_FILE = os.path.join(BASE_DIR, "data_transaksi.csv")

# sistem autentikasi
class SistemAuth:
    def __init__(self, user_account_file=USERS_FILE):
 
        self.user_account_file = user_account_file
        
        if not os.path.exists(self.user_account_file):
            with open(self.user_account_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["username", "password", "nama_kasir"])
    
    def signup(self, username, password, nama_kasir):
        if self._is_username_exists(username):
            return False, "Username telah digunakan"
        
        with open(self.user_account_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([username, password, nama_kasir])
        return True, "Signup berhasil"

    def login(self, username, password):
        with open(self.user_account_file, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["username"] == username and row["password"] == password:
                    return True, row["nama_kasir"]
        return False, "Username atau password salah"

    def _is_username_exists(self, username):
        try:
            with open(self.user_account_file, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["username"] == username:
                        return True
        except:
            pass
        return False

# sistem kasir
class SistemKasir:
    def __init__(self):
        self.keranjang = [] 
        self.metode_pembayaran = "" 
        self.menu_kafe = { 
            "Kopi": {
                "Espresso": 10000,
                "Americano": 12000,
                "Cappucino": 15000,
                "Latte": 15000,
                "Macchiato": 17000,
                "Kopi Tubruk": 8000,
            },
            "Smoothie": {
                "Smoothie Kiwi": 17000,
                "Smoothie Berrie": 18000,
                "Smoothie Alpukat": 16000,
            },
            "Pasta": {
                "Spagetti": 20000,
                "Fettuccine": 22000,
                "Lasagna": 25000,
            },
            "Nasi dan Mie": {
                "Nasi Goreng": 15000,
                "Mie Goreng": 15000,
                "Mie Kuah": 15000,
            },
            "Camilan": {
                "Kentang Goreng": 12000,
                "Onion Rings": 12000,
            },
            "Dessert": {
                "Es Krim": 10000,
                "Puding": 8000,
                "Tart Lemon": 15000,
                "Cheesecake": 15000,
                "Gelato": 12000,
            }
        }
        self.csv_file = TRANSAKSI_FILE
        self._init_csv_file()

    def _init_csv_file(self):
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["No_Struk", "Tanggal", "Waktu", "Kasir", "Menu", 
                               "Kategori", "Harga_Satuan", "Jumlah", "Subtotal", 
                               "Total_Transaksi", "Metode_Pembayaran"])
    
    def get_kategori_menu(self):
        return list(self.menu_kafe.keys())
    
    def get_menu_by_kategori(self, kategori):
        return self.menu_kafe.get(kategori, {})
    
    def tambah_item(self, kategori, nama_menu, jumlah):
        if kategori not in self.menu_kafe:
            return {"status": False, "message": f"Kategori '{kategori}' tidak ditemukan!"}
        
        if nama_menu not in self.menu_kafe[kategori]:
            return {"status": False, "message": f"Menu '{nama_menu}' tidak ditemukan!"}
        
        if jumlah <= 0:
            return {"status": False, "message": "Jumlah harus lebih dari 0!"}
        
        harga = self.menu_kafe[kategori][nama_menu]
        subtotal = harga * jumlah
        
        for item in self.keranjang:
            if item["menu"] == nama_menu:
                item["jumlah"] += jumlah
                item["subtotal"] = item["jumlah"] * item["harga"]
                return {"status": True, "message": f"{nama_menu} ditambahkan lagi."}

        self.keranjang.append({
            "kategori": kategori,
            "menu": nama_menu,
            "harga": harga,
            "jumlah": jumlah,
            "subtotal": subtotal
        })
        
        return {"status": True, "message": f"{nama_menu} x {jumlah} berhasil ditambahkan!"}
    
    def hapus_item(self, index):
        if index < 0 or index >= len(self.keranjang):
            return {"status": False, "message": "Index tidak valid"}
        
        item = self.keranjang.pop(index)
        return {"status": True, "message": f"{item['menu']} dihapus"}
    
    def update_jumlah_item(self, index, jumlah_baru):
        if index < 0 or index >= len(self.keranjang):
            return {"status": False, "message": "Index tidak valid"}
        
        if jumlah_baru <= 0:
            return self.hapus_item(index)
        
        item = self.keranjang[index]
        item["jumlah"] = jumlah_baru
        item["subtotal"] = item["harga"] * jumlah_baru
        return {"status": True, "message": f"{item['menu']} diperbarui"}
    
    def get_keranjang(self):
        return self.keranjang
    
    def hitung_total(self):
        return sum(item["subtotal"] for item in self.keranjang)
    
    def set_metode_pembayaran(self, metode):
        metode_valid = ["Tunai", "QRIS", "Debit"]
        if metode not in metode_valid:
            return {"status": False, "message": "Metode pembayaran tidak valid"}
        
        self.metode_pembayaran = metode
        return {"status": True, "message": "Metode pembayaran diperbarui"}
    
    def get_metode_pembayaran(self):
        return self.metode_pembayaran
    
    def membuat_struk(self, nama_kasir="Kasir"):
        if not self.keranjang:
            return "Keranjang kosong, tidak ada transaksi"
        
        now = datetime.now()
        struk = "=" * 23 + "\n"
        struk += "          STRUK PEMBAYARAN\n"
        struk += "           BREWALYTICA CAFE\n"
        struk += "=" * 23 + "\n\n"
        struk += f"Tanggal: {now.strftime('%d-%m-%Y')}\n"
        struk += f"Waktu  : {now.strftime('%H:%M:%S')}\n"
        struk += f"Kasir  : {nama_kasir}\n"
        struk += "=" * 23 + "\n"
        
        for item in self.keranjang:
            struk += f"{item['menu']} x {item['jumlah']}\n"
            struk += f" Rp {item['harga']:,} = Rp {item['subtotal']:,}\n"
        
        total = self.hitung_total()
        struk += "=" * 23 + "\n"
        struk += f"Total : Rp {total:,}\n"
        struk += f"Metode: {self.metode_pembayaran}\n"
        struk += "=" * 23 + "\n"
        struk += "Terima kasih!\n"
        struk += "=" * 23 + "\n"
        
        return struk
    
    def _membuat_no_struk(self):
        hari_ini = datetime.now().strftime("%Y%m%d")
        count = 0
        
        try:
            with open(self.csv_file, "r", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    if row["No_Struk"].startswith(f"-{hari_ini}"):
                        count += 1
        except:
            pass
        
        return f"-{hari_ini}-{count+1:04d}"
    
    def simpan_transaksi(self, nama_kasir="Kasir"):
        if not self.keranjang:
            return {"status": False, "message": "Keranjang kosong"}
        
        no_struk = self._membuat_no_struk()
        now = datetime.now()
        total = self.hitung_total()

        try:
            with open(self.csv_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                for item in self.keranjang:
                    writer.writerow([
                        no_struk,
                        now.strftime("%Y-%m-%d"),
                        now.strftime("%H:%M:%S"),
                        nama_kasir,
                        item["menu"],
                        item["kategori"],
                        item["harga"],
                        item["jumlah"],
                        item["subtotal"],
                        total,
                        self.metode_pembayaran
                    ])
            return {"status": True, "nomor_struk": no_struk}
        except Exception as e:
            return {"status": False, "message": str(e)}
    
    def selesai_transaksi(self, nama_kasir="Kasir"):
        if not self.keranjang:
            return {"status": False, "message": "Keranjang kosong"}
        
        struk = self.membuat_struk(nama_kasir)
        result = self.simpan_transaksi(nama_kasir)
        
        if not result["status"]:
            return result
        
        self.keranjang = []
        self.metode_pembayaran = ""
        
        return {
            "status": True,
            "struk": struk,
            "nomor_struk": result["nomor_struk"]
        }
    
    def reset_keranjang(self):
        self.keranjang = []
        self.metode_pembayaran = ""
        return {"status": True, "message": "Keranjang dikosongkan"}

# sistem analisis
class SistemAnalisis:
    def __init__(self, csv_file=TRANSAKSI_FILE):
        self.csv_file = csv_file
    
    def _load_data(self):
        if not os.path.exists(self.csv_file):
            return pd.DataFrame()

        df = pd.read_csv(self.csv_file, encoding="utf-8", on_bad_lines="skip")

        if df.empty:
            return df

        df["Tanggal"] = df["Tanggal"].astype(str).str.strip()
        df["Tanggal"] = pd.to_datetime(
            df["Tanggal"],
            format="%Y-%m-%d",
            errors="coerce"
        )
        df["Subtotal"] = pd.to_numeric(df["Subtotal"], errors="coerce")
        df["Jumlah"] = pd.to_numeric(df["Jumlah"], errors="coerce")
        df = df.dropna(subset=["Subtotal", "Jumlah"])

        return df

    def tren_mingguan(self):
        df = self._load_data()
        if df.empty:
            return pd.Series(dtype=float)

        hari_ini = datetime.now().date()
        minggu_lalu = hari_ini - timedelta(days=6)

        df = df[df["Tanggal"].dt.date >= minggu_lalu]
        if df.empty:
            return pd.Series(dtype=float)

        df_group = df.groupby(df["Tanggal"].dt.strftime("%a"))["Subtotal"].sum()

        urutan_hari = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        df_group = df_group.reindex(urutan_hari, fill_value=0)

        return df_group

    def tren_bulanan(self, bulan=None, tahun=None):
        df = self._load_data()
        if df.empty:
            return pd.Series(dtype=float)

        if tahun is None:
            tahun = df['Tanggal'].dt.year.max()

        df = df[df["Tanggal"].dt.year == tahun]
        if df.empty:
            return pd.Series(dtype=float)

        df_group = (df.groupby(df["Tanggal"].dt.month)["Subtotal"].sum().reindex(range(1, 13), fill_value=0))

        nama_bulan = {
            1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
            5: "Mei", 6: "Jun", 7: "Jul", 8: "Agu",
            9: "Sep", 10: "Okt", 11: "Nov", 12: "Des"
        }

        df_group.index = df_group.index.map(nama_bulan)

        return df_group

    def analisis_mingguan(self):
        df = self._load_data()
        if df.empty:
            return {"status": False, "message": "Belum ada data transaksi"}
        
        hari_ini = datetime.now().date()
        minggu_lalu = hari_ini - timedelta(days=7)
        
        df_satu_minggu = df[df["Tanggal"].dt.date >= minggu_lalu]
        
        if df_satu_minggu.empty:
            return {"status": True, "total": 0, "jumlah_item": 0}
        
        total_pendapatan = df_satu_minggu["Subtotal"].sum()
        total_item_terjual = df_satu_minggu["Jumlah"].sum()
        
        return {
            "status": True,
            "total": int(total_pendapatan),
            "jumlah_item": int(total_item_terjual),
            "rentang": f"{minggu_lalu} s.d. {hari_ini}"
        }
    
    def analisis_bulanan(self, bulan=None, tahun=None):
        df = self._load_data()
        if df.empty:
            return {"status": False, "message": "Belum ada data transaksi"}
        
        sekarang = datetime.now()
        if bulan is None:
            bulan = sekarang.month
        if tahun is None:
            tahun = sekarang.year
        
        df_month = df[(df["Tanggal"].dt.month == bulan) & (df["Tanggal"].dt.year == tahun)]

        if df_month.empty:
            return {"status": True, "total": 0, "jumlah_item": 0}
        
        total_pendapatan = df_month["Subtotal"].sum()
        total_item_terjual = df_month["Jumlah"].sum()
        
        return {
            "status": True,
            "bulan": bulan,
            "tahun": tahun,
            "total": int(total_pendapatan),
            "jumlah_item": int(total_item_terjual)
        }

class AuthController:
    def __init__(self, auth_system, main_app):
        self.auth_system = auth_system
        self.main_app = main_app
    
    def handle_login(self, username, password):
        if not username or not password:
            return False, "Username dan password harus diisi"
        
        success, result = self.auth_system.login(username, password)
        if success:
            self.main_app.current_kasir = result
            return True, result
        return False, result
    
    def handle_signup(self, username, password, nama_kasir):
        if not username or not password or not nama_kasir:
            return False, "Semua persyaratan harus diisi"
        
        return self.auth_system.signup(username, password, nama_kasir)

class KasirController:
    def __init__(self, sistem_kasir, main_app):
        self.sistem_kasir = sistem_kasir
        self.main_app = main_app
    
    def tambah_ke_keranjang(self, kategori, menu, jumlah):
        try:
            jumlah_int = int(jumlah)
            return self.sistem_kasir.tambah_item(kategori, menu, jumlah_int)
        except ValueError:
            return {"status": False, "message": "Jumlah harus berupa angka"}
    
    def hapus_dari_keranjang(self, index):
        return self.sistem_kasir.hapus_item(index)
    
    def proses_pembayaran(self, metode):
        if not metode or metode == "Pilih Metode":
            return {"status": False, "message": "Pilih metode pembayaran terlebih dahulu"}
        
        result = self.sistem_kasir.set_metode_pembayaran(metode)
        if not result["status"]:
            return result
        
        return self.sistem_kasir.selesai_transaksi(self.main_app.current_kasir)

class AnalisisController:
    def __init__(self, sistem_analisis):
        self.sistem_analisis = sistem_analisis
    
    def get_tren_mingguan(self):
        return self.sistem_analisis.tren_mingguan()

    def get_tren_bulanan(self, bulan=None, tahun=None):
        return self.sistem_analisis.tren_bulanan(bulan, tahun)

    def get_analisis_mingguan(self):
        return self.sistem_analisis.analisis_mingguan()
    
    def get_analisis_bulanan(self, bulan=None, tahun=None):
        return self.sistem_analisis.analisis_bulanan(bulan, tahun)

class GUILogin(QWidget):
    
    def __init__(self, controller, main_app):
        super().__init__()
        self.controller = controller
        self.main_app = main_app
        
        self.setWindowTitle("Login Kasir")
        
        self.setup_layout()
        self.setup_stylesheet()
        self.setup_connections()
    
    def setup_layout(self):
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 20)
        self.layout.setVerticalSpacing(12)
        
        self.label_title = QLabel("LOGIN")
        self.label_title.setObjectName("title")
        self.label_title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label_title, 0, 0, 1, 2)
        
        self.layout.addWidget(QLabel("Username:"), 1, 0)
        self.input_username = QLineEdit()
        self.layout.addWidget(self.input_username, 2, 0, 1, 2)
        
        self.layout.addWidget(QLabel("Password:"), 3, 0)
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Normal)
        self.layout.addWidget(self.input_password, 4, 0, 1, 2)
    
        self.button_login = QPushButton("Login")
        self.button_login.setObjectName("loginButton")
        self.layout.addWidget(self.button_login, 5, 0, 1, 2)
        
        self.button_signup = QPushButton("Buat Akun")
        self.button_signup.setObjectName("signupButton")
        self.layout.addWidget(self.button_signup, 6, 0, 1, 2, alignment=Qt.AlignCenter)
    
    def setup_stylesheet(self):
        BLUEBERRY = "#2C3F70"
        STRAWBERRY = "#A5231C"
        BUTTERCREAM = "#C8D4E5"
        VIOLET = "#8089D2"
        MERINGE = "#E8EBED"
        
        self.setStyleSheet(f"""
        QWidget {{
            background-color: {MERINGE};
        }}

        QLabel#title {{
            font-size: 40px;
            font-weight: bold;
            color: {BLUEBERRY};
            margin-bottom: 10px;
        }}
        
        QLineEdit {{
            padding: 10px;
            border-radius: 8px;
            border: 1px solid {BUTTERCREAM};
            background-color: white;
            font-size: 16px;
        }}
        
        QLineEdit:focus {{
            border: 1px solid {VIOLET};
        }}
        
        QPushButton#loginButton {{
            background-color: {BLUEBERRY};
            color: white;
            padding: 12px;
            border-radius: 8px;
            font-size: 18px;
            font-weight: bold;
        }}
        
        QPushButton#loginButton:hover {{
            background-color: {VIOLET};
        }}
        
        QPushButton#signupButton {{
            border: none;
            background: transparent;
            color: {STRAWBERRY};
            text-decoration: underline;
            font-size: 14px;
        }}
        """)

    def reset_form(self):
        self.input_username.clear()
        self.input_password.clear()
    
    def setup_connections(self):
        self.button_login.clicked.connect(self.handle_login)
        self.button_signup.clicked.connect(self.go_to_signup)
    
    def handle_login(self):
        username = self.input_username.text()
        password = self.input_password.text()
        
        success, message = self.controller.handle_login(username, password)
        
        if success:
            QMessageBox.information(self, "Berhasil", f"Selamat datang, {message}!")
            self.main_app.go_to_kasir()
        else:
            QMessageBox.warning(self, "Gagal", message)
    
    def go_to_signup(self):
        self.main_app.go_to_signup()


class GUISignup(QWidget):
    
    def __init__(self, controller, main_app):
        super().__init__()
        self.controller = controller
        self.main_app = main_app
        
        self.setWindowTitle("Sign Up Kasir")
        
        self.setup_layout()
        self.setup_stylesheet()
        self.setup_connections()

    def setup_layout(self):
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(40, 10, 40, 20)
        self.layout.setVerticalSpacing(14)
    
        self.button_exit_arrow = QPushButton("⟵", self)
        self.button_exit_arrow.setObjectName("exitbutton")
        self.button_exit_arrow.setGeometry(10, 10, 50, 50)

        self.label_title = QLabel("SIGN UP")
        self.label_title.setObjectName("title")
        self.label_title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label_title, 0, 0, 1, 2)

        self.input_nama = QLineEdit()
        self.input_nama.setPlaceholderText("Nama Kasir")
        self.layout.addWidget(self.input_nama, 1, 0, 1, 2)

        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Username")
        self.layout.addWidget(self.input_username, 2, 0, 1, 2)

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Password")
        self.input_password.setEchoMode(QLineEdit.Normal)
        self.layout.addWidget(self.input_password, 3, 0, 1, 2)

        self.button_signup = QPushButton("Sign Up")
        self.button_signup.setObjectName("signupbutton")
        self.layout.addWidget(self.button_signup, 4, 0, 1, 2)
    

    def setup_connections(self):
        self.button_signup.clicked.connect(self.handle_signup)
        self.button_exit_arrow.clicked.connect(self.go_to_login)
    
    def handle_signup(self):
        nama = self.input_nama.text()
        username = self.input_username.text()
        password = self.input_password.text()
        
        success, message = self.controller.handle_signup(username, password, nama)
        
        if success:
            if success:
                QMessageBox.information(self, "Berhasil", "Akun berhasil dibuat! Silakan login.")
                self.go_to_login()
        else:
            QMessageBox.warning(self, "Gagal", message)
    
    def go_to_login(self):
        self.main_app.login_page.reset_form()
        self.main_app.go_to_login()

    def setup_stylesheet(self):
        BLUEBERRY = "#2C3F70"
        STRAWBERRY = "#A5231C"
        BUTTERCREAM = "#C8D4E5"
        VIOLET = "#8089D2"
        MERINGE = "#E8EBED"
        
        self.setStyleSheet(f"""
        QWidget {{
            background-color: {MERINGE};
        }}
        
        QPushButton#exitbutton {{
            background: transparent;
            border: none;
            font-size: 24px;
            color: {BLUEBERRY};
        }}
        
        QPushButton#exitbutton:hover {{
            color: {STRAWBERRY};
        }}
        
        QLabel#title {{
            font-size: 40px;
            font-weight: bold;
            color: {BLUEBERRY};
            margin-bottom: 5px;
        }}
        
        QLineEdit {{
            padding: 10px;
            border-radius: 8px;
            border: 1px solid {BUTTERCREAM};
            background-color: white;
            font-size: 14px;
        }}
        
        QLineEdit:focus {{
            border: 1px solid {VIOLET};
        }}
        
        QPushButton#signupbutton {{
            background-color: {BLUEBERRY};
            color: white;
            padding: 12px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
        }}
        
        QPushButton#signupbutton:hover {{
            background-color: {VIOLET};
        }}
        """)

class GUIKasir(QWidget):
    
    def __init__(self, controller, main_app):
        super().__init__()
        self.controller = controller
        self.main_app = main_app

        self.setWindowTitle("Kasir Brewalytica")
        
        self.setup_layout()
        self.setup_stylesheet()
        self.setup_connections()
    

    def setup_layout(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(12)
        
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(64)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 6, 12, 6)
        
        title = QLabel("BREWALYTICA CAFE")
        title.setObjectName('title_login')
        header_layout.addWidget(title)
        header_layout.addStretch(1)
        
        self.cashier_label = QLabel(f"Kasir: {self.main_app.current_kasir}")
        self.cashier_label.setObjectName('cashier_label')
        header_layout.addWidget(self.cashier_label)
        
        self.button_analisis = QPushButton("Analisis")
        self.button_analisis.setObjectName('button_analisis')
        header_layout.addWidget(self.button_analisis)
        
        self.button_logout = QPushButton("Logout")
        self.button_logout.setObjectName('button_logout')
        header_layout.addWidget(self.button_logout)
        
        main_layout.addWidget(header)

        body_layout = QHBoxLayout()
        body_layout.setSpacing(12)

        left_panel = QFrame()
        left_panel.setObjectName('left_panel')
        left_panel.setFixedWidth(380)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(18, 18, 18, 18)
        left_layout.setSpacing(12)
        
        header_left = QLabel("INPUT PESANAN")
        header_left.setObjectName('header_left')
        header_left.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(header_left)

        left_layout.addWidget(QLabel("Kategori:"))
        self.kategori_cb = QComboBox()
        self.kategori_cb.setObjectName('combo_box')
        self.kategori_cb.setFixedHeight(31)
        self.kategori_cb.addItem("Pilih Kategori")
        for kat in self.controller.sistem_kasir.get_kategori_menu():
            self.kategori_cb.addItem(kat)
            self.kategori_cb.setObjectName('combo_box')
        left_layout.addWidget(self.kategori_cb)

        left_layout.addWidget(QLabel("Menu:"))
        self.menu_cb = QComboBox()
        self.menu_cb.setObjectName('combo_box')
        self.menu_cb.addItem("Pilih Menu")
        self.menu_cb.setFixedHeight(31)
        left_layout.addWidget(self.menu_cb)

        left_layout.addWidget(QLabel("Jumlah:"))
        self.jumlah_barang = QLineEdit()
        self.jumlah_barang.setPlaceholderText("Masukkan jumlah barang")
        left_layout.addWidget(self.jumlah_barang)

        self.btn_tambah = QPushButton("+  TAMBAH KE KERANJANG")
        self.btn_tambah.setObjectName('button_tambah')
        left_layout.addWidget(self.btn_tambah)

        left_layout.addWidget(QLabel("Metode Pembayaran:"))
        self.metode_cb = QComboBox()
        self.metode_cb.setObjectName('combo_box')
        self.metode_cb.addItems(["Pilih Metode", "Tunai", "QRIS", "Debit"])
        left_layout.addWidget(self.metode_cb)
        
        left_layout.addStretch(1)
        body_layout.addWidget(left_panel)

        right_panel = QFrame()
        right_panel.setObjectName('right_panel')
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(12, 12, 12, 12)
        
        header_right = QLabel("KERANJANG BELANJA")
        header_right.setObjectName('header_right')
        right_layout.addWidget(header_right)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Kategori", "Menu", "Jumlah", "Harga", "Subtotal"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        right_layout.addWidget(self.table)

        self.btn_hapus = QPushButton("HAPUS ITEM TERPILIH")
        self.btn_hapus.setObjectName('button_hapus')
        right_layout.addWidget(self.btn_hapus, alignment=Qt.AlignCenter)

        self.total_label = QLabel("TOTAL: Rp 0")
        self.total_label.setObjectName('total_label')
        self.total_label.setStyleSheet("")
        self.total_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.total_label)

        self.btn_proses = QPushButton("PROSES PEMBAYARAN")
        self.btn_proses.setObjectName('button_proses')
        right_layout.addWidget(self.btn_proses)
        
        body_layout.addWidget(right_panel, 1)
        main_layout.addLayout(body_layout)
    
    def setup_stylesheet(self):
        BLUEBERRY = "#2C3F70"
        STRAWBERRY = "#A5231C"
        BUTTERCREAM = "#C8D4E5"
        VIOLET = "#8089D2"
        MERINGE = "#E8EBED"
        BIRU = "#a5c6db"
        HIJAU = "#2ca86b"
        TOSCA = "#E1FFFF"
        PUTIH = "#FFFFFF"
        BIRU_TUA = "#035590"

        self.setStyleSheet(f"""
        QWidget {{
            background-color: {MERINGE};
        }}
        
        QFrame#header{{
            background-color: {VIOLET}; 
            border-radius:4px;
        }}
                           
        QLabel#title_login{{
            background-color:{VIOLET}; 
            color:{MERINGE}; 
            font:16pt 'Cooper Black'; 
            font-weight:600;
        }}
                           
        QLabel#cashier_label{{
            color:{MERINGE}; 
            background-color:{VIOLET}; 
            padding:4px 8px; 
            border-radius:6px; 
            font: 11pt 'Cooper Black';
        }}
                           
        QPushButton#button_analisis{{
            background-color:{BIRU}; 
            border-radius:16px; 
            font:14pt 'Cooper Black';
            color:{MERINGE}; 
            padding:6px 12px
        }}
        
        QPushButton#button_logout{{
            background-color:{STRAWBERRY}; 
            border-radius:16px; 
            font:14pt 'Cooper Black'; 
            color:{MERINGE}; 
            padding:6px 12px
        }}
                           
        QFrame#left_panel{{
            background-color:{MERINGE}; 
            border-radius:4px; 
            color:{BLUEBERRY};
        }}

        QLabel#header_left{{
            font-weight:700; 
            font-size:14pt; 
            color:{BLUEBERRY};
        }}

        QPushButton#button_tambah {{
            background:{HIJAU};
            color:{MERINGE};
            padding:12px;
            border-radius:6px;
            font-weight:700;
        }}

        QFrame#right_panel {{
            background:{MERINGE}; 
            border-radius:4px;
            color:{BLUEBERRY};
        }}   
        
        QLabel#header_right {{
            font-weight:700; 
            font-size:13pt; 
            color:{BLUEBERRY};
        }}
        
        QPushButton#button_hapus {{
            background-color:{STRAWBERRY}; 
            border-radius:16px; 
            font:14pt 'Cooper Black'; 
            color:{MERINGE}; 
            padding:8px;
        }}

        QLabel#total_label {{
            font-weight:700; 
            color:#c43a2c; 
            font-size:14pt;
        }}
        
        QPushButton#button_proses {{
            background-color:{BIRU}; 
            border-radius:16px; 
            font:14pt 'Cooper Black'; 
            color:{MERINGE}; padding:14px;
        }}

        QComboBox#combo_box {{
            background-color: {MERINGE};
            color: {BLUEBERRY};
            border: 0.5px solid {BUTTERCREAM};
        }}

        QComboBox#combo_box:hover {{
            background-color: {BUTTERCREAM};
        }}

        QComboBox#combo_box:focus {{
            border: 0.5px solid {BLUEBERRY};
        }}
""")
    
    def setup_connections(self):
        self.kategori_cb.currentIndexChanged.connect(self.update_menu_options)
        self.btn_tambah.clicked.connect(self.tambah_keranjang)
        self.btn_hapus.clicked.connect(self.hapus_item)
        self.btn_proses.clicked.connect(self.proses_pembayaran)
        self.button_logout.clicked.connect(self.logout)
        self.button_analisis.clicked.connect(self.go_to_analisis)
    
    def update_menu_options(self):
        kategori = self.kategori_cb.currentText()
        self.menu_cb.clear()
        self.menu_cb.addItem("Pilih Menu")
        
        if kategori != "Pilih Kategori":
            menu_dict = self.controller.sistem_kasir.get_menu_by_kategori(kategori)
            for menu_name in menu_dict.keys():
                self.menu_cb.addItem(menu_name)
    
    def tambah_keranjang(self):
        kategori = self.kategori_cb.currentText()
        menu = self.menu_cb.currentText()
        jumlah = self.jumlah_barang.text()
        
        if kategori == "Pilih Kategori" or menu == "Pilih Menu":
            QMessageBox.warning(self, "Error", "Pilih kategori dan menu terlebih dahulu!")
            return
        
        result = self.controller.tambah_ke_keranjang(kategori, menu, jumlah)
        
        if result["status"]:
            self.refresh_table()
            self.update_total()
            self.jumlah_barang.clear()
            QMessageBox.information(self, "Berhasil", result["message"])
        else:
            QMessageBox.warning(self, "Gagal", result["message"])
    
    def refresh_table(self):
        self.table.setRowCount(0)
        keranjang = self.controller.sistem_kasir.get_keranjang()
        
        for item in keranjang:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(item["kategori"]))
            self.table.setItem(r, 1, QTableWidgetItem(item["menu"]))
            self.table.setItem(r, 2, QTableWidgetItem(str(item["jumlah"])))
            self.table.setItem(r, 3, QTableWidgetItem(f"Rp {item['harga']:,}"))
            self.table.setItem(r, 4, QTableWidgetItem(f"Rp {item['subtotal']:,}"))
    
    def hapus_item(self):
        selected = self.table.currentRow()
        
        if selected < 0:
            QMessageBox.warning(self, "Error", "Pilih item yang ingin dihapus!")
            return
        
        result = self.controller.hapus_dari_keranjang(selected)
        
        if result["status"]:
            self.refresh_table()
            self.update_total()
            QMessageBox.information(self, "Berhasil", result["message"])
        else:
            QMessageBox.warning(self, "Gagal", result["message"])
    
    def update_total(self):
        total = self.controller.sistem_kasir.hitung_total()
        self.total_label.setText(f"TOTAL: Rp {total:,}")
    
    def proses_pembayaran(self):
        metode = self.metode_cb.currentText()
        
        result = self.controller.proses_pembayaran(metode)
        
        if result["status"]:
            struk = result["struk"]
            QMessageBox.information(self, "Transaksi Berhasil", f"Nomor Struk: {result['nomor_struk']}\n\n{struk}")
            self.refresh_table()
            self.update_total()
            self.metode_cb.setCurrentIndex(0)
        else:
            QMessageBox.warning(self, "Gagal", result["message"])
    
    def logout(self):
        reply = QMessageBox.question(self, "Konfirmasi", "Yakin ingin logout?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.controller.sistem_kasir.reset_keranjang()
            self.main_app.go_to_login()
    
    def go_to_analisis(self):
        self.main_app.go_to_analisis()

class GUIAnalisis(QWidget):
    
    def __init__(self, controller, main_app):
        super().__init__()
        self.controller = controller
        self.main_app = main_app
        
        self.setWindowTitle("Analisis Penjualan")
        
        self.setup_layout()
        self.setup_stylesheet()
        self.setup_connections()
    
    def setup_layout(self):
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setHorizontalSpacing(20)
        self.layout.setVerticalSpacing(20)

        self.label_title = QLabel("ANALISIS PENJUALAN")
        self.label_title.setObjectName("headerTitle")
        self.layout.addWidget(self.label_title, 0, 0)
        
        self.btn_back = QPushButton("KEMBALI")
        self.btn_back.setObjectName("backBtn")
        self.layout.addWidget(self.btn_back, 0, 1, alignment=Qt.AlignRight)

        self.btn_weekly = QPushButton("ANALISIS MINGGUAN")
        self.btn_weekly.setObjectName("analyzeBtn")
        self.layout.addWidget(self.btn_weekly, 1, 0)
        
        self.btn_monthly = QPushButton("ANALISIS BULANAN")
        self.btn_monthly.setObjectName("analyzeBtn")
        self.layout.addWidget(self.btn_monthly, 1, 1)

        self.fig = Figure(figsize=(8, 5))
        self.canvas = FigureCanvas(self.fig)
        self.layout.addWidget(self.canvas, 3, 0, 1, 2)
    
    def setup_stylesheet(self):
        BLUEBERRY = "#2C3F70"
        STRAWBERRY = "#A5231C"
        BUTTERCREAM = "#C8D4E5"
        MERINGE = "#E8EBED"
        
        self.setStyleSheet(f"""
        QWidget {{
            background-color: {MERINGE};
        }}
        
        QLabel#headerTitle {{
            font-size: 22px;
            font-weight: bold;
            color: {BLUEBERRY};
        }}
        
        QPushButton#backBtn {{
            background-color: {STRAWBERRY};
            color: {MERINGE};
            padding: 6px 14px;
            border-radius: 6px;
            font-weight: bold;
        }}
        
        QPushButton#analyzeBtn {{
            background-color: {BLUEBERRY};
            color: {MERINGE};
            padding: 10px;
            border-radius: 6px;
            font-weight: bold;
        }}
        
        QPushButton#analyzeBtn:hover {{
            background-color: {BUTTERCREAM};
            color: {BLUEBERRY};
        }}
        """)
    
    def setup_connections(self):
        self.btn_back.clicked.connect(self.go_back)
        self.btn_weekly.clicked.connect(self.show_analisis_mingguan)
        self.btn_monthly.clicked.connect(self.show_analisis_bulanan)
    
    def show_analisis_mingguan(self):
        data = self.controller.get_tren_mingguan()

        if data.empty or data.sum() == 0:
            QMessageBox.warning(self, "Peringatan", "Belum ada data transaksi minggu ini")
            return

        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.ticklabel_format(style='plain', axis='y')

        ax.plot(data.index, data.values, marker='o', linewidth=2)
        ax.set_title("Trend Penjualan 7 Hari Terakhir", fontweight="bold")
        ax.set_xlabel("Hari")
        ax.set_ylabel("Total Penjualan (Rp)")
        ax.grid(True)

        self.canvas.draw()
    def show_analisis_bulanan(self):
        data = self.controller.get_tren_bulanan()

        if data.empty or data.sum() == 0:
            QMessageBox.warning(self, "Peringatan", "Belum ada data transaksi bulan ini")
            return

        self.fig.clear()
        ax = self.fig.add_subplot(111)

        ax.bar(data.index, data.values)
        ax.set_title("Trend Penjualan Bulanan", fontweight="bold")
        ax.set_xlabel("Bulan")
        ax.set_ylabel("Total Penjualan (Rp)")
        ax.ticklabel_format(style='plain', axis='y')

        self.canvas.draw()

    def go_back(self):
        self.main_app.go_to_kasir()

class MainApp(QWidget):

    def __init__(self):
        super().__init__()

        self.auth_system = SistemAuth()
        self.sistem_kasir = SistemKasir()
        self.sistem_analisis = SistemAnalisis()

        self.current_kasir = "Guest"

        self.auth_controller = AuthController(self.auth_system, self)
        self.kasir_controller = KasirController(self.sistem_kasir, self)
        self.analisis_controller = AnalisisController(self.sistem_analisis)

        self.login_page = GUILogin(self.auth_controller, self)
        self.signup_page = GUISignup(self.auth_controller, self)
        self.kasir_page = GUIKasir(self.kasir_controller, self)
        self.analisis_page = GUIAnalisis(self.analisis_controller, self)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.signup_page)
        self.stack.addWidget(self.kasir_page)
        self.stack.addWidget(self.analisis_page)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.stack)

        self.setWindowTitle("Sistem Kasir Brewalytica")
        self.resize(500, 400)
        self.setMinimumSize(500, 400)
        self.setStyleSheet("background-color: #E8EBED;")

        self.stack.setCurrentWidget(self.login_page)

    def go_to_login(self):
        self.stack.setCurrentWidget(self.login_page)
        self.resize(500, 400)

    def go_to_signup(self):
        self.stack.setCurrentWidget(self.signup_page)
        self.resize(500, 400)

    def go_to_kasir(self):
        self.kasir_page.cashier_label.setText(f"Kasir: {self.current_kasir}")
        self.stack.setCurrentWidget(self.kasir_page)
        self.resize(1200, 800)

    def go_to_analisis(self):
        self.stack.setCurrentWidget(self.analisis_page)
        self.resize(900, 600)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    main_window = MainApp()
    main_window.show()

    sys.exit(app.exec_())