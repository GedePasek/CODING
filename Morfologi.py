import numpy as np
from PIL import Image, ExifTags
import os
import sys
import cv2

def resize_citra_biner(img_array, max_width=300):
    h, w = img_array.shape[:2]

    if w > max_width:
        rasio = max_width / w
        dimensi_baru = (max_width, int(h * rasio))
        
        # cv2.INTER_NEAREST wajib digunakan untuk citra biner agar tidak muncul piksel abu-abu
        img_resized = cv2.resize(img_array, dimensi_baru, interpolation=cv2.INTER_NEAREST)
        return img_resized
        
    return img_array

def baca_dan_proses_gambar(image_path):
    try:
        img = Image.open(image_path)
        img_color_array = np.array(img)
        
        # Konversi ke Grayscale dan pastikan bentuknya 2D
        if len(img_color_array.shape) == 3:
            h, w, c = img_color_array.shape
            gray_array = np.zeros((h, w), dtype=np.uint8)
            for y in range(h):
                for x in range(w):
                    r, g, b = img_color_array[y, x, :3]
                    gray_array[y, x] = int(0.299 * r + 0.587 * g + 0.114 * b)
            img_array = gray_array
        else:
            img_array = img_color_array
            
        # Konversi ke biner (0 dan 255) agar operasi morfologi bekerja optimal
        img_biner = np.where(img_array > 127, 255, 0).astype(np.uint8)
        return img_biner
    except Exception as e:
        print(f"Gagal membaca gambar: {e}")
        return None

# ==========================================
# FUNGSI MANUAL MORFOLOGI CITRA DIGITAL
# ==========================================

def manual_dilation(img_array, radius=5):
    h, w = img_array.shape
    out = np.zeros((h, w), dtype=np.uint8)
    
    for y in range(radius, h - radius):
        for x in range(radius, w - radius):
            maks_val = 0
            for i in range(-radius, radius + 1):
                for j in range(-radius, radius + 1):
                    if img_array[y + i, x + j] > maks_val:
                        maks_val = img_array[y + i, x + j]
            out[y, x] = maks_val
    return out

def manual_erosion(img_array, radius=5):
    h, w = img_array.shape
    out = np.zeros((h, w), dtype=np.uint8)
    
    # Menggunakan radius untuk menentukan batas margin agar tidak error di tepi gambar
    for y in range(radius, h - radius):
        for x in range(radius, w - radius):
            min_val = 255
            # Menggunakan radius untuk memperbesar ukuran kernel (misal radius=5 berarti kernel 11x11)
            for i in range(-radius, radius + 1):
                for j in range(-radius, radius + 1):
                    if img_array[y + i, x + j] < min_val:
                        min_val = img_array[y + i, x + j]
            out[y, x] = min_val
    return out

def manual_opening(img_array):
    eroded = manual_erosion(img_array)
    dilated = manual_dilation(eroded)
    return dilated

def manual_closing(img_array, radius=30):
    dilated = manual_dilation(img_array, radius=radius)
    eroded = manual_erosion(dilated, radius=radius)
    return eroded

def manual_hit_or_miss(img_array):
    # Kernel contoh untuk mendeteksi sudut pojok kanan-atas
    kernel_j = np.array([[0, 0, 1], 
                         [0, 1, 0], 
                         [0, 0, 0]])
    kernel_k = np.array([[1, 1, 0], 
                         [1, 0, 0], 
                         [0, 0, 0]])
    
    h, w = img_array.shape
    out = np.zeros((h, w), dtype=np.uint8)
    bin_img = (img_array > 127).astype(int)
    
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            match = True
            for i in range(-1, 2):
                for j in range(-1, 2):
                    p = bin_img[y + i, x + j]
                    kj = kernel_j[i + 1, j + 1]
                    kk = kernel_k[i + 1, j + 1]
                    
                    if kj == 1 and p != 1:
                        match = False
                    if kk == 1 and p != 0:
                        match = False
            if match:
                out[y, x] = 255
    return out

def manual_skeletonization(img_array):
    curr = (img_array > 127).astype(np.uint8) * 255
    skel = np.zeros_like(curr)
    
    while np.any(curr > 0):
        eroded = manual_erosion(curr, radius=1)
        opened = manual_dilation(eroded, radius=1)

        subset = curr.astype(int) - opened.astype(int)
        subset[subset < 0] = 0

        skel = np.maximum(skel, subset.astype(np.uint8))
        curr = eroded.copy()

        cv2.imwrite("hasil_skeleton.png", skel)
    return skel

# ==========================================
# MENU UTAMA PROGRAM
# ==========================================

def main():
    while True:
        print("\n" + "="*45)
        print(" MENU UTAMA OPERASI MORFOLOGI CITRA")
        print("="*45)
        print("1. Dilasi (Dilation)")
        print("2. Erosi (Erosion)")
        print("3. Opening")
        print("4. Closing")
        print("5. Hit-or-Miss")
        print("6. Skeletonization (Penulangan)")
        print("0. Keluar Program")
        print("="*45)
        
        pilihan = input("Masukkan nomor operasi yang ingin dilakukan: ").strip()
        
        if pilihan == '0':
            print("Keluar dari program. Terima kasih")
            break
            
        if pilihan in ['1', '2', '3', '4', '5', '6']:
            image_path = input("Masukkan nama file atau path foto yang ingin diproses (contoh: piring.jpg): ").strip()
            
            if not os.path.exists(image_path):
                print(f"Error: File '{image_path}' tidak ditemukan di direktori ini!")
                continue
                
            print("Sedang memproses citra secara manual, mohon tunggu sebentar...")
            img_biner = baca_dan_proses_gambar(image_path)
            
            if img_biner is None:
                continue
                
            # Eksekusi sesuai pilihan user
            if pilihan == '1':
                hasil = manual_dilation(img_biner)
                judul = "Hasil Dilasi"
            elif pilihan == '2':
                hasil = manual_erosion(img_biner)
                judul = "Hasil Erosi"
            elif pilihan == '3':
                hasil = manual_opening(img_biner)
                judul = "Hasil Opening"
            elif pilihan == '4':
                hasil = manual_closing(img_biner)
                judul = "Hasil Closing"
            elif pilihan == '5':
                hasil = manual_hit_or_miss(img_biner)
                judul = "Hasil Hit-or-Miss"
            elif pilihan == '6':
                hasil = manual_skeletonization(img_biner)
                judul = "Hasil Skeletonization"
                
            # Tampilkan hasil gambar
            print(f"Berhasil! Menampilkan {judul}...")
            Image.fromarray(hasil).show()
        else:
            print("Pilihan tidak valid. Silakan masukkan angka 0 sampai 6.")

if __name__ == "__main__":
    main()