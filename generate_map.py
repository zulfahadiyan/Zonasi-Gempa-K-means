import pandas as pd
import folium
from sklearn.cluster import KMeans
import os
import shutil

# --- 1. PERSIAPAN DATA ---
print("Sedang memproses data...")
try:
    df = pd.read_csv('katalog_gempa_v2.tsv', sep='\t')
    df = df[['latitude', 'longitude', 'magnitude', 'depth']].dropna()
    df = df[df['magnitude'] >= 3.0] 

    # Spatial Grouping
    df['lat_group'] = df['latitude'].round(1)
    df['lon_group'] = df['longitude'].round(1)

    df_grouped = df.groupby(['lat_group', 'lon_group']).agg({
        'magnitude': 'max',
        'depth': 'mean'
    }).reset_index()

except FileNotFoundError:
    print("❌ Eits! File katalog_gempa_v2.tsv belum diupload.")
    df_grouped = pd.DataFrame({'lat_group':[-7], 'lon_group':[110], 'magnitude':[5], 'depth':[50]})

# --- 2. ANALISIS CLUSTERING ---
if len(df_grouped) >= 3:
    kmeans = KMeans(n_clusters=3, random_state=42)
    df_grouped['cluster'] = kmeans.fit_predict(df_grouped[['depth']])
else:
    df_grouped['cluster'] = 0

# --- 3. PROSES LOGO (Cek nama file) ---
if not os.path.exists('public'):
    os.makedirs('public')

logo_path = "logo_ugm_hitamputih.png" 
logo_html_tag = "" 

if os.path.exists(logo_path):
    shutil.copy(logo_path, f'public/{logo_path}')
    logo_html_tag = f'<img src="{logo_path}" width="60px" style="margin-bottom: 5px;">'
    print(f"✅ Logo '{logo_path}' dipakai.")
else:
    print(f"⚠️ Logo '{logo_path}' tidak ada. Pakai logo online.")
    logo_html_tag = '<img src="https://upload.wikimedia.org/wikipedia/id/2/25/Logo_UGM.png" width="60px" style="margin-bottom: 5px;">'

# --- 4. VISUALISASI PETA ---
print("Sedang mendesain tampilan dashboard...")

center_lat = df_grouped['lat_group'].mean()
center_lon = df_grouped['lon_group'].mean()

m = folium.Map(location=[center_lat, center_lon], zoom_start=5, tiles='CartoDB dark_matter')

def get_color(depth):
    if depth <= 60: return '#00ff00'   # Hijau
    elif depth <= 300: return '#ffff00' # Kuning
    else: return '#ff0000'             # Merah

for idx, row in df_grouped.iterrows():
    depth = row['depth']
    mag = row['magnitude']
    color = get_color(depth)
    kategori = "Dangkal" if depth <=60 else "Menengah" if depth <=300 else "Dalam"
    
    folium.CircleMarker(
        location=[row['lat_group'], row['lon_group']],
        radius=mag * 1.5,
        color=color, fill=True, fill_color=color, fill_opacity=0.7, weight=0.5,
        popup=f"<b>Mag: {mag} SR</b><br>Depth: {int(depth)} km<br>({kategori})"
    ).add_to(m)

# --- 5. PANEL INFORMASI (FINAL) ---
info_panel = f'''
<div style="
    position: fixed; 
    top: 10px; right: 10px; width: 300px; 
    max-height: 90vh; overflow-y: auto;
    background-color: rgba(255, 255, 255, 0.95); 
    padding: 15px; border-radius: 10px; 
    border: 1px solid #ddd; 
    box-shadow: 0px 0px 10px rgba(0,0,0,0.5); 
    z-index: 9999; font-family: sans-serif;
">
    <div style="text-align: center; margin-bottom: 15px;">
        <h3 style="margin:0; color:#222; font-size:16px; font-weight:bold;">PETA SEBARAN GEMPA</h3>
        <span style="font-size:11px; color:#555;">Analisis Clustering (K-Means)</span>
    </div>

    <div style="text-align: center; font-size: 11px; color: #333; margin-bottom: 10px; background-color: #f9f9f9; padding: 8px; border-radius: 5px;">
        <b style="display:block; margin-bottom:5px;">Dibuat oleh:</b>
        <div style="margin-bottom:4px;">
            <b>M. Firdaus Ar Riza</b><br>
            23/514435/TK/56484
        </div>
        <div style="margin-bottom:4px;">
            <b>Daffa Laksa Adi Y.</b><br>
            23/516605/TK/56797
        </div>
        <div>
            <b>Zulfa Hadiyan T.</b><br>
            23/516792/TK/56818
        </div>
    </div>

    <hr style="border: 0; border-top: 1px solid #ccc; margin: 10px 0;">

    <h4 style="margin:0 0 8px 0; font-size:13px; color:#333;">📖 Legenda</h4>
    <div style="font-size:11px; margin-bottom:10px;">
        <b>Kedalaman (Warna):</b><br>
        <span style="color:#00ff00;">●</span> Dangkal (< 60 km)<br>
        <span style="color:#ffff00;">●</span> Menengah (60-300 km)<br>
        <span style="color:#ff0000;">●</span> Dalam (> 300 km)
    </div>
    <div style="font-size:11px;">
        <b>Kekuatan (Ukuran):</b><br>
        <div style="display:flex; align-items:center; margin-top:2px;">
            <div style="width:15px; text-align:center;"><div style="width:4px; height:4px; background:#555; border-radius:50%; margin:auto;"></div></div>
            <div style="margin-left:5px;">Kecil (3-4 SR)</div>
        </div>
        <div style="display:flex; align-items:center; margin-top:2px;">
            <div style="width:15px; text-align:center;"><div style="width:8px; height:8px; background:#555; border-radius:50%; margin:auto;"></div></div>
            <div style="margin-left:5px;">Sedang (5-6 SR)</div>
        </div>
        <div style="display:flex; align-items:center; margin-top:2px;">
            <div style="width:15px; text-align:center;"><div style="width:12px; height:12px; background:#555; border-radius:50%; margin:auto;"></div></div>
            <div style="margin-left:5px;">Besar (> 7 SR)</div>
        </div>
    </div>

    <hr style="border: 0; border-top: 1px solid #ccc; margin: 10px 0;">

    <div style="font-size:10px; color:#666; margin-bottom: 15px;">
        <b>Sumber Data:</b><br>
        Katalog Gempa BMKG & USGS
    </div>

    <div style="text-align: center; font-size:10px; color:#444; border-top: 2px solid #eee; padding-top: 10px;">
        {logo_html_tag}
        <br>
        <div style="font-weight: bold; margin-top: 5px;">
            PROGRAM STUDI SARJANA TEKNIK GEODESI<br>
            DEPARTEMEN TEKNIK GEODESI<br>
            FAKULTAS TEKNIK<br>
            UNIVERSITAS GADJAH MADA
        </div>
    </div>

</div>
'''
m.get_root().html.add_child(folium.Element(info_panel))

# --- 6. SIMPAN ---
m.save('public/index.html')
print("✅ SELESAI! Footer Institusi sekarang sudah BOLD semua.")
