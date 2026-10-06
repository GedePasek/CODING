import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage import transform

# Cukup ganti nama file gambar di sini saja
image_path = 'mejakerja.jpg'  # Ganti dengan nama file gambar yang ingin diproses

# 1. BACA GAMBAR
img_raw = cv2.imread(image_path)
if img_raw is None:
    raise ValueError(f"Gambar '{image_path}' tidak ditemukan. Pastikan nama file dan path sudah benar.")

# 2. RESIZE OTOMATIS BERBASIS SISI TERPANJANG (ASPECT RATIO 100% TERJAGA)
# Menstandarkan sisi terpanjang ke 400 piksel agar skala geometri selalu konsisten
TARGET_MAX_DIM = 400
h_raw, w_raw = img_raw.shape[:2]
scale_factor = TARGET_MAX_DIM / max(h_raw, w_raw)

new_w = int(w_raw * scale_factor)
new_h = int(h_raw * scale_factor)
img_color = cv2.resize(img_raw, (new_w, new_h), interpolation=cv2.INTER_AREA)

# Hitung dimensi diagonal untuk referensi persentase parameter
diag = np.sqrt(new_w**2 + new_h**2)

# Konversi warna & Grayscale
img_rgb = cv2.cvtColor(img_color, cv2.COLOR_BGR2RGB)
img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)

#clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
#img_enhanced = clahe.apply(img_gray)

# Blur adaptif agar tekstur halus/noise tereduksi
img_blurred = cv2.GaussianBlur(img_gray, (9, 9), 1.0)

# 3. DETEKSI TEPI (CANNY)
edges_cv2 = cv2.Canny(img_blurred, 45, 120)

# Siapkan kanvas salinan
img_lines = img_rgb.copy()
img_circles = img_rgb.copy()
img_ellipses = img_rgb.copy()

# =========================================================================
# A. HOUGH LINES (GARIS) - PARAMETER OTOMATIS
# =========================================================================
# Garis minimal panjangnya 10% dari diagonal gambar
min_line_len = int(diag * 0.10)
max_line_gap = int(diag * 0.02)

lines = cv2.HoughLinesP(edges_cv2, 1, np.pi/180, threshold=50, 
                        minLineLength=min_line_len, maxLineGap=max_line_gap)
if lines is not None:
    for line in lines:
        x1, y1, x2, y2 = line.flatten()
        cv2.line(img_lines, (x1, y1), (x2, y2), (255, 0, 0), 2)

# =========================================================================
# B. HOUGH CIRCLES (LINGKARAN) - DIPERKETAT & SELEKTIF
# =========================================================================
# Radius dibatasi agar tidak mendeteksi lingkaran raksasa fiktif
min_radius = int(diag * 0.03)   # ~3% diagonal (lingkaran kecil/sedang)
max_radius = int(diag * 0.16)   # ~16% diagonal (maksimal seukuran lingkaran oranye bawah)
min_dist = int(diag * 0.10)     # Jarak antar lingkaran diperlebar agar tidak menumpuk

circles = cv2.HoughCircles(
    img_blurred, 
    cv2.HOUGH_GRADIENT, 
    dp=1.2, 
    minDist=min_dist,
    param1=210,     # Ambang batas atas detektor Canny internal
    param2=50,      # DIPERKETAT: hanya mendeteksi bentuk lingkaran yang solid & jelas
    minRadius=min_radius, 
    maxRadius=max_radius
)

if circles is not None:
    circles = np.uint16(np.around(circles))
    for i in circles[0, :]:
        # Gambar keliling lingkaran (hijau)
        cv2.circle(img_circles, (i[0], i[1]), i[2], (0, 255, 0), 2)
        # Gambar titik pusat (merah)
        cv2.circle(img_circles, (i[0], i[1]), 3, (255, 0, 0), -1)
    print(f"Ditemukan {len(circles[0])} lingkaran yang presisi.")
else:
    print("Tidak ditemukan lingkaran yang memenuhi kriteria ketat.")

# =========================================================================
# C. HOUGH ELLIPSE (ELIPS) - ADAPTIF, CEPAT & TIDAK AKAN HANG
# =========================================================================
y_pts, x_pts = np.nonzero(edges_cv2)
total_edge_points = len(y_pts)

# Batasi input titik tepi maksimal ~300 titik secara dinamis
step = max(1, total_edge_points // 300)

edges_sparse = np.zeros_like(edges_cv2, dtype=bool)
edges_sparse[y_pts[::step], x_pts[::step]] = True

print(f"Sedang memproses Hough Ellipse ({np.sum(edges_sparse)} titik sampel)...")

# Ukuran elips proporsional
min_ellipse_size = int(diag * 0.03)
max_ellipse_size = int(diag * 0.30)

result_ellipses = transform.hough_ellipse(
    edges_sparse,
    threshold=10,
    accuracy=2,
    min_size=min_ellipse_size,
    max_size=max_ellipse_size
)

if len(result_ellipses) > 0:
    result_ellipses.sort(order='accumulator')
    
    # Ambil elips terbaik yang bukan garis degenerasi
    valid_ellipse = None
    for rec in reversed(result_ellipses):
        val = tuple(rec)
        yc, xc, a, b = (int(round(x)) for x in val[1:5])
        orientation = val[5]
        
        if a > 0 and b > 0:
            ratio = min(a, b) / max(a, b)
            # Hindari elips yang terlalu tipis menyerupai garis (ratio < 0.25)
            if ratio >= 0.25:
                valid_ellipse = (xc, yc, a, b, orientation)
                break
                
    if valid_ellipse:
        xc, yc, a, b, ori = valid_ellipse
        cv2.ellipse(img_ellipses, (xc, yc), (a, b), int(np.degrees(ori)), 0, 360, (0, 0, 255), 2)
        print(f"Elips berhasil terdeteksi pada koordinat ({xc}, {yc})!")
    else:
        print("Elips terdeteksi namun terindikasi garis lurus.")
else:
    print("Tidak ditemukan elips.")

# =========================================================================
# 4. TAMPILKAN HASIL
# =========================================================================
fig, axes = plt.subplots(2, 3, figsize=(14, 9))
ax = axes.ravel()

titles = [
    '1. Citra Asli (Auto-Scaled)',
    '2. Pre-processing (Grayscale)',
    '3. Deteksi Tepi (Canny)',
    '4. Hough Transform Garis',
    '5. Hough Transform Lingkaran',
    '6. Hough Transform Elips'
]
images = [img_rgb, img_gray, edges_cv2, img_lines, img_circles, img_ellipses]

for i in range(6):
    cmap = 'gray' if i in [1, 2] else None
    ax[i].imshow(images[i], cmap=cmap)
    ax[i].set_title(titles[i])
    ax[i].axis('off')

plt.tight_layout()
plt.show()