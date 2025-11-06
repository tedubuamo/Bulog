import streamlit as st

def show():
    st.title("🏠 Selamat Datang di Aplikasi Sentral Pangan")

    st.write("""
        <p style="color:#FFFFFF; text-align: justify;">
            Aplikasi ini dikembangkan untuk melakukan analisis dan prediksi pergerakan harga pangan di Provinsi Jawa Timur dengan menggunakan 
            data yang diperoleh dari Badan Pangan Nasional (Bapanas). Beberapa fitur utama aplikasi ini antara lain:
        </p>

        <p style="color:#FFFFFF; text-align: justify;">
            - Halaman Scraping Data: Mengambil data harga konsumen dan produsen melalui API terbuka, dengan opsi untuk menarik data harian 
            maupun untuk periode tertentu. Fitur ini memungkinkan pengguna untuk mengakses informasi harga komoditas pangan secara terperinci.
        </p>

        <p style="color:#FFFFFF; text-align: justify;">
            - Halaman Insight: Menyediakan ringkasan harga komoditas berdasarkan kota atau kabupaten di Provinsi Jawa Timur, sehingga memberikan wawasan 
            yang lebih mendalam mengenai pergerakan harga di tingkat lokal.
        </p>

        <p style="color:#FFFFFF; text-align: justify;">
            - Halaman Forecasting: Memungkinkan pengguna untuk memproyeksikan harga pangan hingga enam bulan ke depan. Fitur ini dilengkapi 
            dengan visualisasi grafik dan tabel prediksi yang memudahkan pengguna untuk menganalisis tren harga komoditas.
        </p>

        <p style="color:#FFFFFF; text-align: justify;">
            - Halaman Monitoring Harga Pangan Real-Time: Menyajikan informasi harga pangan secara real-time, memungkinkan pematauan 
            harga dengan cepat dan tepat.
        </p>
    """, unsafe_allow_html=True)

    st.write(""" 
        <p style="color:#FFFFFF; text-align: justify;">
            📊 <b>Data Harga Komoditas:</b>
        </p>
        <p style="color:#FFFFFF; text-align: justify;">
            Aplikasi ini memanfaatkan data harga komoditas yang diperoleh dari website Bapanas, yang menyediakan informasi terkait 
            harga berbagai komoditas pangan di Indonesia. Data harga pangan dapat diakses pada link berikut <a href=" https://panelharga.badanpangan.go.id/tabel-rerata">Data Komoditas Pangan Bapanas</a>.
        </p>
    """, unsafe_allow_html=True)

    st.write("""
    ---
    <p style="color:#FFFFFF; text-align: justify;">
            📝 Aplikasi ini dikembangkan oleh © Ardiansyah Indra Febrianto
    </p>
    """, unsafe_allow_html=True)