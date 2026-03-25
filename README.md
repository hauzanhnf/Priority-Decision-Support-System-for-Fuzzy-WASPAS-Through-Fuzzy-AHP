# Priority Decision Support System for Poverty Reduction Using Fuzzy WASPAS Through Fuzzy AHP in Ponorogo Regency
Priority Decision Support System for Poverty Reduction Using Fuzzy WASPAS Through Fuzzy AHP in Ponorogo Regency

**Penulis:** Hauzan Hanifah Zahra
**Studi Kasus:** Kabupaten Ponorogo

## Deskripsi Proyek
Penyaluran bantuan sosial seringkali menghadapi kendala ketidaktepatan sasaran (kesalahan inklusi dan eksklusi) akibat subjektivitas dalam penilaian manual melalui musyawarah desa. Sistem ini mengusulkan pendekatan *Multi Criteria Decision Making* (MCDM) berbasis logika *fuzzy* untuk menentukan prioritas penanganan kemiskinan yang objektif, transparan, dan adaptif. Penelitian ini juga berhasil memetakan fenomena sosiologis ***asset rich, cash poor*** di Kabupaten Ponorogo, di mana kemiskinan kini lebih dominan ditentukan oleh aspek Sosial Ekonomi dan Pendidikan dibandingkan sekadar kualitas fisik hunian rumah.

## Metodologi
Sistem ini menggunakan metode hybrid MCDM:
1. **Fuzzy Analytical Hierarchy Process (Fuzzy AHP):** Digunakan untuk menghitung dan menentukan bobot prioritas dari 14 indikator kemiskinan (berdasarkan standar BPS dan DTKS) guna mengatasi ketidakpastian dan ambiguitas penilaian dari pakar,. 
2. **Fuzzy Weighted Aggregated Sum Product Assessment (Fuzzy WASPAS):** Digunakan untuk mengevaluasi, memeringkat, dan mengklasifikasikan 20.000 data rumah tangga ke dalam segmentasi prioritas perlindungan sosial (Desil 1 hingga Desil 4).

## Fitur Utama Aplikasi
Aplikasi ini dibangun menggunakan *framework* antarmuka **Streamlit**, yang terdiri dari 4 halaman utama:
*   🗄️ **Halaman Database:** Pusat tampilan data yang memuat 20.000 rekaman keluarga beserta 14 indikator kemiskinan, dilengkapi dengan fitur pencarian dan penyaringan data,.
*   ⚙️ **Halaman Penilaian:** Modul otomatisasi di mana pengguna dapat mengunggah (*upload*) data keluarga dalam format Excel (`.xlsx`). Sistem akan otomatis menghitung nilai *Fuzzy WASPAS* dan menentukan segmentasi desilnya,.
*   📊 **Halaman Dashboard:** Menyajikan visualisasi interaktif dan pemetaan spasial (GIS) untuk melihat sebaran "zona merah" kemiskinan di berbagai kecamatan,.
*   📝 **Halaman Inputasi:** Menyediakan formulir (*form*) untuk memasukkan data keluarga baru secara manual. Sistem akan seketika memprediksi klaster prioritas (Desil) untuk keluarga tersebut,.

## Performa Model
Model *decision support system* ini telah diuji langsung di lapangan menggunakan teknik **Blind Expert Validation** bersama Pendamping PKH dan Dinas Sosial Kabupaten Ponorogo,.
*   **Akurasi Kesesuaian Lapangan:** 89,92%
*   **Tingkat Kesepakatan (*Cohen's Kappa*):** 0,857 (Kategori Sangat Kuat)

## Struktur Data
Sistem ini menggunakan 14 sub kriteria kemiskinan yang terbagi dalam 4 kriteria utama:
*   **Sandang Pangan** (Frekuensi Makan, Konsumsi Daging/Susu, Beli Pakaian)
*   **Sosial Ekonomi Pendidikan** (Pendapatan, Tabungan/Simpanan, Pendidikan Kepala Keluarga, Akses Berobat)
*   **Akses Utilitas** (Sumber Penerangan, Bahan Bakar Masak, Sumber Air Minum)
*   **Kualitas Hunian** (Fasilitas BAB, Luas Lantai, Jenis Dinding, Jenis Lantai)
