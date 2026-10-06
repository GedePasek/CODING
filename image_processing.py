import os

# --- FITUR OTOMATIS PINDAH PATH KE FOLDER SKRIP ---
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"[*] Direktori aktif berhasil dipindahkan ke: {script_dir}")
except Exception as e:
    print(f"[!] Gagal mengubah direktori otomatis: {e}")
# --------------------------------------------------

try:
    from PIL import Image, ExifTags
except ImportError:
    print("Library 'Pillow' tidak ditemukan. Silakan install dengan perintah: pip install Pillow")
    exit()

def analyze_image(image_path):
    print("\n" + "="*50)
    print("            ANALISIS PROPERTI CITRA")
    print("="*50)
    
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' tidak ditemukan.")
        return None

    try:
        img = Image.open(image_path)
        img.load()
        
        print(f"1. Path File     : {image_path}")
        print(f"2. Format File   : {img.format} ({img.format_description})")
        print(f"3. Resolusi      : {img.width} x {img.height} pixels (Lebar x Tinggi)")
        print(f"4. Mode Warna    : {img.mode}")
        
        # Deteksi Kedalaman dan Intensitas
        if img.mode == '1':
            print("5. Kedalaman     : 1 bit per pixel\n6. Intensitas    : 2 nilai (0 dan 1) -> Citra Biner")
        elif img.mode == 'L':
            print("5. Kedalaman     : 8 bit per pixel\n6. Intensitas    : 256 nilai (0-255) -> Citra Grayscale")
        elif img.mode == 'P':
            print("5. Kedalaman     : 8 bit per pixel\n6. Intensitas    : 256 nilai warna -> Citra Palet")
        elif img.mode == 'RGB':
            print("5. Kedalaman     : 24 bit (8 bit per channel R,G,B)\n6. Intensitas    : ~16.7 juta kombinasi warna")
        elif img.mode == 'RGBA':
            print("5. Kedalaman     : 32 bit (24 bit RGB + 8 bit Alpha)\n6. Intensitas    : ~16.7 juta warna + transparansi")
        else:
            print(f"5. Kedalaman     : Bergantung pada mode khusus ({img.mode})")
            
        # Deteksi Operasi Geometri / Rotasi EXIF
        try:
            exif = img._getexif()
            orientation_str = "Normal / Tidak ada data rotasi"
            if exif is not None:
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation] == 'Orientation':
                        break
                if orientation in exif:
                    val = exif[orientation]
                    if val == 2: orientation_str = "Dicerminkan Horizontal (Flipped)"
                    elif val == 3: orientation_str = "Diputar 180 Derajat"
                    elif val == 4: orientation_str = "Dicerminkan Vertikal"
                    elif val == 6: orientation_str = "Diputar 90 Derajat (Searah Jarum Jam)"
                    elif val == 8: orientation_str = "Diputar 90 Derajat (Berlawanan Arah Jarum Jam)"
            print(f"7. Orientasi EXIF: {orientation_str}")
        except Exception:
            print("7. Orientasi EXIF: Tidak dapat dibaca")
            
        return img.convert("RGB")
    except Exception as e:
        print(f"Gagal membaca citra: {e}")
        return None

def clamp(value):
    return max(0, min(255, int(round(value))))

def tampilkan_dan_simpan(img_obj, nama_file_output):
    try:
        img_obj.save(nama_file_output)
        print(f"[!] Gambar berhasil disimpan permanen di folder ini sebagai: {nama_file_output}")
        if os.name == 'nt':
            os.startfile(nama_file_output)
        else:
            img_obj.show()
    except Exception as e:
        print(f"Gagal membuka atau menyimpan gambar: {e}")

def cetak_matriks_angka(img):
    print("\n" + "-"*50)
    print(" MATRIKS PIKSEL CITRA (TAMPILAN ANGKA GRAYSCALE)")
    print("-"*50)
    
    gray_img = img.convert('L')
    pixels = gray_img.load()
    width, height = gray_img.size
    
    print(f"Resolusi maksimal gambar ini adalah {width} (Lebar) x {height} (Tinggi).")
    try:
        req_w = int(input(f"Berapa lebar kolom piksel yang ingin dicetak? (maksimal {width}): "))
        req_h = int(input(f"Berapa tinggi baris piksel yang ingin dicetak? (maksimal {height}): "))
    except ValueError:
        print("Input tidak valid. Menampilkan ukuran default 10x10.")
        req_w, req_h = 10, 10
        
    # Pastikan ukuran tidak melebihi resolusi asli
    max_w = min(abs(req_w), width)
    max_h = min(abs(req_h), height)
    
    print(f"\nMenampilkan cuplikan matriks {max_w}x{max_h} dari area pojok kiri atas:\n")
    
    for y in range(max_h):
        baris_teks = []
        for x in range(max_w):
            nilai_piksel = pixels[x, y]
            baris_teks.append(f"{nilai_piksel:3}")
        print(" ".join(baris_teks))
        
    if max_w < width or max_h < height:
        print("\n(Ada sisa piksel yang disembunyikan sesuai batas yang Anda masukkan)")

def manual_operations_menu(image_path):
    img = analyze_image(image_path)
    if not img:
        return

    width, height = img.size
    pixels = img.load() 

    while True:
        print("\n" + "="*50)
        print("           PILIH OPERASI CITRA (MANUAL)")
        print("="*50)
        print("1. Tampilkan Citra Asli & Info Properti")
        print("2. Rotasi 90 Derajat")
        print("3. Flip Horizontal")
        print("4. Citra Negatif / Inversi")
        print("5. Grayscale")
        print("6. Brightness / Kecerahan")
        print("7. Contrast / Kontras")
        print("8. Thresholding / Binerisasi")
        print("9. Tampilkan Matriks Piksel (Bentuk Angka)")
        print("0. Keluar Program")
        print("="*50)
        
        pilihan = input("Masukkan nomor operasi yang ingin dilakukan: ")
        
        if pilihan == '0':
            print("Terima kasih, keluar dari program...")
            break
            
        elif pilihan == '1':
            tampilkan_dan_simpan(img, "hasil_01_asli.jpg")
            
        elif pilihan == '2':
            print("Memproses Rotasi 90 Derajat (Manual)...")
            rotated_img = Image.new('RGB', (height, width))
            rotated_pixels = rotated_img.load()
            for x in range(width):
                for y in range(height):
                    new_x = height - y - 1
                    new_y = x
                    rotated_pixels[new_x, new_y] = pixels[x, y]
            tampilkan_dan_simpan(rotated_img, "hasil_02_rotasi.jpg")

        elif pilihan == '3':
            print("Memproses Flip Horizontal (Manual)...")
            flipped_img = Image.new('RGB', (width, height))
            flipped_pixels = flipped_img.load()
            for x in range(width):
                for y in range(height):
                    new_x = width - x - 1
                    flipped_pixels[new_x, y] = pixels[x, y]
            tampilkan_dan_simpan(flipped_img, "hasil_03_flip.jpg")

        elif pilihan == '4':
            print("Memproses Citra Negatif / Inversi (Manual)...")
            inverted_img = Image.new('RGB', (width, height))
            inverted_pixels = inverted_img.load()
            for x in range(width):
                for y in range(height):
                    r, g, b = pixels[x, y]
                    inverted_pixels[x, y] = (255 - r, 255 - g, 255 - b)
            tampilkan_dan_simpan(inverted_img, "hasil_04_negatif.jpg")

        elif pilihan == '5':
            print("Memproses Grayscale (Manual)...")
            grayscale_img = Image.new('L', (width, height))
            grayscale_pixels = grayscale_img.load()
            for x in range(width):
                for y in range(height):
                    r, g, b = pixels[x, y]
                    gray_val = int(0.299 * r + 0.587 * g + 0.114 * b)
                    grayscale_pixels[x, y] = clamp(gray_val)
            tampilkan_dan_simpan(grayscale_img, "hasil_05_grayscale.jpg")

        elif pilihan == '6':
            try:
                tambah = int(input("Masukkan nilai penambahan kecerahan (misal 50 atau -50): "))
            except ValueError:
                print("Input tidak valid. Menggunakan nilai default +50.")
                tambah = 50
                
            print(f"Memproses Kecerahan {tambah} (Manual)...")
            bright_img = Image.new('RGB', (width, height))
            bright_pixels = bright_img.load()
            for x in range(width):
                for y in range(height):
                    r, g, b = pixels[x, y]
                    bright_pixels[x, y] = (
                        clamp(r + tambah), 
                        clamp(g + tambah), 
                        clamp(b + tambah)
                    )
            tampilkan_dan_simpan(bright_img, "hasil_06_brightness.jpg")

        elif pilihan == '7':
            try:
                C = float(input("Masukkan tingkat kontras (C, contoh: 50 atau -50): "))
            except ValueError:
                print("Input tidak valid. Menggunakan nilai default 50.")
                C = 50.0
                
            print(f"Memproses Kontras {C} (Manual)...")
            F = (259.0 * (C + 255.0)) / (255.0 * (259.0 - C))
            contrast_img = Image.new('RGB', (width, height))
            contrast_pixels = contrast_img.load()
            for x in range(width):
                for y in range(height):
                    r, g, b = pixels[x, y]
                    contrast_pixels[x, y] = (
                        clamp(F * (r - 128) + 128),
                        clamp(F * (g - 128) + 128),
                        clamp(F * (b - 128) + 128)
                    )
            tampilkan_dan_simpan(contrast_img, "hasil_07_contrast.jpg")

        elif pilihan == '8':
            try:
                threshold = int(input("Masukkan nilai Threshold (batas pemisah 0-255, contoh 128): "))
            except ValueError:
                print("Input tidak valid. Menggunakan nilai default 128.")
                threshold = 128
                
            print(f"Memproses Thresholding batas {threshold} (Manual)...")
            thresh_img = Image.new('L', (width, height)) 
            thresh_pixels = thresh_img.load()
            for x in range(width):
                for y in range(height):
                    r, g, b = pixels[x, y]
                    gray_val = int(0.299 * r + 0.587 * g + 0.114 * b)
                    if gray_val >= threshold:
                        thresh_pixels[x, y] = 255
                    else:
                        thresh_pixels[x, y] = 0
            tampilkan_dan_simpan(thresh_img, "hasil_08_threshold.jpg")

        elif pilihan == '9':
            cetak_matriks_angka(img)

        else:
            print("Pilihan tidak valid. Silakan masukkan nomor menu yang benar.")

if __name__ == "__main__":
    print("="*50)
    print("PROGRAM PENGOLAHAN CITRA MANUAL")
    print("="*50)
    
    while True:
        print("\nMasukkan nama file atau path lengkap gambar yang ingin diproses.")
        print("(Pastikan file benar-benar ada di komputer Anda. Ketik 'exit' untuk keluar)")
        file_gambar = input("Path File Gambar: ").strip()
        
        if file_gambar.lower() == 'exit':
            print("Keluar dari program...")
            break
            
        if not file_gambar:
            print("[!] Input tidak boleh kosong! Silakan masukkan nama file/path yang benar.")
            continue
            
        if not os.path.exists(file_gambar):
            print(f"[!] Error: File '{file_gambar}' tidak ditemukan.")
            continue
            
        print(f"\n[+] File '{file_gambar}' berhasil ditemukan! Memuat citra...")
        manual_operations_menu(file_gambar)
        break