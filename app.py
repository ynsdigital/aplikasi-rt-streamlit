import streamlit as st
import sqlite3
import pandas as pd
from passlib.hash import bcrypt # Untuk hashing password
import os
from datetime import datetime

# --- PENGATURAN HALAMAN ---
st.set_page_config(page_title="Sistem Data Warga", page_icon="🏘️", layout="wide")

# =================================================================================
# BAGIAN 1: PENGATURAN DATABASE (SQLite)
# =================================================================================

def init_db():
    """Inisialisasi database dan membuat tabel jika belum ada."""
    conn = sqlite3.connect('warga.db')
    c = conn.cursor()
    # Tabel untuk pengguna (login)
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    ''')
    # Tabel untuk data warga dengan kolom yang sudah dilengkapi
    c.execute('''
        CREATE TABLE IF NOT EXISTS warga (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            no_kk TEXT,
            nik TEXT UNIQUE,
            nama_lengkap TEXT,
            jenis_kelamin TEXT,
            tanggal_lahir DATE,
            agama TEXT,
            pendidikan TEXT,
            pekerjaan TEXT,
            golongan_darah TEXT,
            status_perkawinan TEXT,
            tanggal_perkawinan DATE,
            nama_ayah TEXT,
            nama_ibu TEXT,
            nama_kepala_keluarga TEXT,
            alamat TEXT,
            rt TEXT,
            rw TEXT,
            tanggal_dikeluarkan DATE
        )
    ''')
    conn.commit()
    conn.close()

# Panggil fungsi inisialisasi di awal
init_db()

# --- Fungsi Bantuan untuk Password ---
def hash_password(password):
    return bcrypt.hash(password)

def verify_password(password, hashed_password):
    return bcrypt.verify(password, hashed_password)

# --- Fungsi Bantuan untuk Database ---
def db_execute(query, params=()):
    conn = sqlite3.connect('warga.db')
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()
    conn.close()

def db_query(query, params=()):
    conn = sqlite3.connect('warga.db')
    c = conn.cursor()
    c.execute(query, params)
    results = c.fetchall()
    conn.close()
    return results

# =================================================================================
# BAGIAN 2: SISTEM AUTENTIKASI (LOGIN, LOGOUT, DAFTAR)
# =================================================================================
# (Bagian ini tidak berubah, jadi kita gunakan yang sudah ada)
def show_login_page():
    """Menampilkan halaman login, daftar, dan lupa password."""
    st.title("🏘️ Sistem Informasi Data Warga")
    
    menu = ["Login", "Daftar Akun", "Lupa Password"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        st.subheader("Silakan Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

            if submitted:
                user = db_query("SELECT * FROM users WHERE username = ?", (username,))
                if user and verify_password(password, user[0][2]):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = user[0][1]
                    st.session_state['role'] = user[0][3]
                    st.rerun()
                else:
                    st.error("Username atau Password salah")

    elif choice == "Daftar Akun":
        st.subheader("Buat Akun Baru")
        with st.form("signup_form"):
            new_username = st.text_input("Username Baru")
            new_password = st.text_input("Password Baru", type="password")
            role = "user" 
            submitted = st.form_submit_button("Daftar")

            if submitted:
                if len(new_password) < 6:
                    st.warning("Password minimal 6 karakter.")
                else:
                    try:
                        hashed_pass = hash_password(new_password)
                        db_execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                                   (new_username, hashed_pass, role))
                        st.success("Akun berhasil dibuat! Silakan login.")
                    except sqlite3.IntegrityError:
                        st.error("Username sudah ada. Silakan pilih username lain.")

    elif choice == "Lupa Password":
        st.subheader("Reset Password")
        st.warning("Untuk saat ini, silakan hubungi Admin (Ketua RT) secara langsung untuk meminta reset password manual.")

# =================================================================================
# BAGIAN 3: APLIKASI UTAMA (SETELAH LOGIN BERHASIL)
# =================================================================================

def show_main_app():
    """Menampilkan aplikasi utama setelah pengguna login."""
    st.sidebar.title(f"Selamat Datang, {st.session_state['username']}!")
    st.sidebar.write(f"Peran Anda: **{st.session_state['role'].upper()}**")
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.header("📝 Form Input Data Warga")
    with st.form("data_warga_form", clear_on_submit=True):
        st.subheader("Informasi Utama")
        col1, col2, col3 = st.columns(3)
        with col1:
            no_kk = st.text_input("Nomor Kartu Keluarga (KK)*", max_chars=16)
            nik = st.text_input("NIK*", max_chars=16)
            nama_lengkap = st.text_input("Nama Lengkap*")
            jenis_kelamin = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
            golongan_darah = st.selectbox("Golongan Darah", ["A", "B", "AB", "O", "Tidak Tahu"])
        with col2:
            tanggal_lahir = st.date_input("Tanggal Lahir", min_value=datetime(1900, 1, 1), value=None)
            agama = st.selectbox("Agama", ["Islam", "Kristen Protestan", "Katolik", "Hindu", "Buddha", "Khonghucu", "Lainnya"])
            pendidikan = st.text_input("Pendidikan Terakhir")
            pekerjaan = st.text_input("Jenis Pekerjaan")
            status_perkawinan = st.selectbox("Status Perkawinan", ["Belum Kawin", "Kawin Tercatat", "Kawin Belum Tercatat", "Cerai Hidup", "Cerai Mati"])
        with col3:
            tanggal_perkawinan = st.date_input("Tanggal Perkawinan (jika sudah kawin)", value=None)
            nama_ayah = st.text_input("Nama Ayah")
            nama_ibu = st.text_input("Nama Ibu")

        st.subheader("Informasi Alamat & KK")
        col_alamat1, col_alamat2 = st.columns(2)
        with col_alamat1:
            alamat = st.text_area("Alamat Lengkap")
            rt = st.text_input("RT", max_chars=3)
            rw = st.text_input("RW", max_chars=3)
        with col_alamat2:
            nama_kepala_keluarga = st.text_input("Nama Kepala Keluarga")
            tanggal_dikeluarkan = st.date_input("Tanggal KK Dikeluarkan", value=None)

        submitted = st.form_submit_button("Simpan Data")
        if submitted:
            # Validasi
            if not no_kk or not nik or not nama_lengkap:
                st.warning("Mohon isi field yang ditandai bintang (*): No. KK, NIK, Nama Lengkap.")
            else:
                try:
                    query_insert = """
                        INSERT INTO warga (
                            no_kk, nik, nama_lengkap, jenis_kelamin, tanggal_lahir, agama, pendidikan, pekerjaan,
                            golongan_darah, status_perkawinan, tanggal_perkawinan, nama_ayah, nama_ibu,
                            nama_kepala_keluarga, alamat, rt, rw, tanggal_dikeluarkan
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    params = (
                        no_kk, nik, nama_lengkap, jenis_kelamin, tanggal_lahir, agama, pendidikan, pekerjaan,
                        golongan_darah, status_perkawinan, tanggal_perkawinan, nama_ayah, nama_ibu,
                        nama_kepala_keluarga, alamat, rt, rw, tanggal_dikeluarkan
                    )
                    db_execute(query_insert, params)
                    st.success("Data warga berhasil disimpan!")
                except sqlite3.IntegrityError:
                    st.error("NIK sudah terdaftar di database.")
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")

    st.divider()

    st.header("📊 Tampilan Hasil Input")
    
    warga_data = db_query("SELECT * FROM warga ORDER BY id DESC")
    if warga_data:
        # Menyesuaikan nama kolom dengan struktur tabel baru
        column_names = [
            'ID', 'No. KK', 'NIK', 'Nama Lengkap', 'Jenis Kelamin', 'Tgl Lahir', 'Agama', 'Pendidikan',
            'Pekerjaan', 'Gol. Darah', 'Status Kawin', 'Tgl Kawin', 'Nama Ayah', 'Nama Ibu',
            'Kepala Keluarga', 'Alamat', 'RT', 'RW', 'Tgl KK Dikeluarkan'
        ]
        df = pd.DataFrame(warga_data, columns=column_names)
        
        if st.session_state['role'] != 'admin':
            st.dataframe(df)
        else:
            st.info("Anda adalah Admin. Anda dapat mengedit dan menghapus data.")

            # Logika untuk mengedit data
            if 'edit_id' not in st.session_state:
                st.session_state.edit_id = None

            col_data, col_edit = st.columns([3, 1])

            with col_data:
                st.dataframe(df)

            with col_edit:
                st.subheader("Aksi")
                id_to_action = st.selectbox("Pilih ID untuk Aksi", df['ID'])
                
                if st.button("✏️ Edit Data Ini"):
                    st.session_state.edit_id = id_to_action
                    st.rerun()
                
                if st.button("❌ Hapus Data Ini", type="primary"):
                    db_execute("DELETE FROM warga WHERE id = ?", (id_to_action,))
                    st.success(f"Data dengan ID {id_to_action} berhasil dihapus.")
                    st.session_state.edit_id = None # Hapus state edit jika ada
                    st.rerun()

            # Form edit akan muncul jika ID edit dipilih
            if st.session_state.edit_id:
                data_to_edit = db_query("SELECT * FROM warga WHERE id = ?", (st.session_state.edit_id,))[0]
                st.divider()
                st.header(f"✏️ Mengedit Data untuk ID: {st.session_state.edit_id}")
                
                with st.form("edit_form"):
                    # Tampilkan data saat ini di form edit
                    # (Ini adalah contoh singkat, Anda bisa melengkapi semua field seperti form input)
                    edit_nama = st.text_input("Nama Lengkap", value=data_to_edit[3])
                    edit_nik = st.text_input("NIK", value=data_to_edit[2])
                    edit_alamat = st.text_area("Alamat", value=data_to_edit[15])
                    # ... Tambahkan semua field lain di sini ...

                    col_btn_edit, col_btn_cancel = st.columns(2)
                    with col_btn_edit:
                        if st.form_submit_button("Simpan Perubahan"):
                            # Query UPDATE
                            query_update = "UPDATE warga SET nama_lengkap=?, nik=?, alamat=? WHERE id=?"
                            params_update = (edit_nama, edit_nik, edit_alamat, st.session_state.edit_id)
                            db_execute(query_update, params_update)
                            st.success("Data berhasil diperbarui!")
                            st.session_state.edit_id = None
                            st.rerun()
                    with col_btn_cancel:
                        if st.form_submit_button("Batal", type="secondary"):
                            st.session_state.edit_id = None
                            st.rerun()

    else:
        st.info("Belum ada data warga yang diinput.")

# =================================================================================
# BAGIAN 4: ALUR UTAMA APLIKASI
# =================================================================================
if st.session_state.get("logged_in", False):
    show_main_app()
else:
    show_login_page()