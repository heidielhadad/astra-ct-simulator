import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt
from PIL import Image
import astra
from skimage.data import shepp_logan_phantom
from skimage.restoration import denoise_tv_chambolle
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import mean_squared_error as mse
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.util import random_noise

# ==========================================
# 1. PAGE CONFIGURATION & UI SETUP
# ==========================================
st.set_page_config(layout="wide", page_title="ASTRA CT Simulator")
st.title("ASTRA-Powered CT Simulator")
st.markdown("Investigating projection sampling density and noise levels using the professional ASTRA Toolbox.")

# ==========================================
# 2. SIDEBAR CONTROLS 
# ==========================================
st.sidebar.header("📁 Data Input")
uploaded_file = st.sidebar.file_uploader("Upload Custom Image", type=["png", "jpg", "jpeg"])

N = 400
M = np.pi/2.0 * N   # Crowther Criterion
max_projections = math.ceil(M/10)*10   # Ceiling the number of maximum projections to fit the slider's 10 steps
st.sidebar.header("⚙️ Acquisition Parameters")
num_projections = st.sidebar.slider("Sampling Density (Projections)", 10, max_projections, 180, step=10)
noise_variance = st.sidebar.slider("Sinogram Noise Level (Simulated Dose)", 0.0, 0.5, 0.05, step=0.01)

# st.sidebar.header("🧮 Reconstruction Settings")
# # ASTRA has different built-in algorithms. We will use standard FBP for this comparison.
# filter_type = st.sidebar.selectbox("FBP Filter", ['ram-lak', 'shepp-logan', 'hamming', 'hann'])

st.sidebar.header("✨ Correction Techniques")
apply_correction = st.sidebar.checkbox("Apply TV Denoising")
if apply_correction:
    tv_weight = st.sidebar.slider("Denoising Strength", 0.01, 0.50, 0.10, step=0.01)

# ==========================================
# 3. DATA PROCESSING
# ==========================================
@st.cache_data 
def load_default_phantom():
    return shepp_logan_phantom()

@st.cache_data
def process_uploaded_image(upload, size):
    img = Image.open(upload).convert('L')
    img = img.resize((size, size))
    return np.array(img, dtype=np.float32) / 255.0

if uploaded_file is not None:
    image = process_uploaded_image(uploaded_file, N)
else:
    image = load_default_phantom().astype(np.float32)
    

# ==========================================
# 4. THE ASTRA SIMULATION ENGINE
# ==========================================
# Define the physical setup of the scanner
# 1. Volume Geometry (The Patient/Image space)
vol_geom = astra.create_vol_geom(N, N)

# 2. Projection Geometry (The X-ray Tube and Detector space)
# We use a parallel beam geometry here. 
angles = np.linspace(0, np.pi, max(num_projections, 1), endpoint=False)
proj_geom = astra.create_proj_geom('parallel', 1.0, int(np.sqrt(2)*N), angles)

# 3. Create the Projector
projector_id = astra.create_projector('linear', proj_geom, vol_geom)

# --- FORWARD PROJECTION (Acquisition) ---
# This simulates taking the scan and creates the sinogram
sinogram_id, clean_sinogram = astra.create_sino(image, projector_id)

# Introduce controlled noise
if noise_variance > 0:
    noisy_sinogram = random_noise(clean_sinogram, mode='gaussian', var=noise_variance).astype(np.float32)
else:
    noisy_sinogram = clean_sinogram

# --- BACKWARD PROJECTION (Reconstruction) ---
# Create ASTRA data objects to hold our noisy data and the final output
noisy_sino_id = astra.data2d.create('-sino', proj_geom, noisy_sinogram)
recon_id = astra.data2d.create('-vol', vol_geom)

# Configure the FBP algorithm
cfg = astra.astra_dict('FBP')
cfg['ReconstructionDataId'] = recon_id
cfg['ProjectionDataId'] = noisy_sino_id
cfg['ProjectorId'] = projector_id
cfg['FilterType'] = "ram-lak" 

# Run the algorithm
alg_id = astra.algorithm.create(cfg)
astra.algorithm.run(alg_id)

# Extract the mathematical result
reconstruction = astra.data2d.get(recon_id)

# IMPORTANT: ASTRA requires you to manually delete C++ memory objects when done!
astra.algorithm.delete(alg_id)
astra.data2d.delete(recon_id)
astra.data2d.delete(noisy_sino_id)
astra.data2d.delete(sinogram_id)
astra.projector.delete(projector_id)

# ==========================================
# 5. CORRECTION & METRICS
# ==========================================
# Normalize reconstruction for viewing and metric calculation
reconstruction = (reconstruction - np.min(reconstruction)) / (np.max(reconstruction) - np.min(reconstruction) + 1e-8)

if apply_correction:
    final_image = denoise_tv_chambolle(reconstruction, weight=tv_weight)
    status_text = "Reconstructed + TV Denoising"
else:
    final_image = reconstruction
    status_text = "Standard FBP Reconstruction"

final_image_clipped = np.clip(final_image, 0, 1)

score_ssim = ssim(image, final_image_clipped, data_range=1.0)
score_mse = mse(image, final_image_clipped)
score_psnr = psnr(image, final_image_clipped, data_range=1.0)

std_dev = np.std(final_image_clipped)
score_cnr = np.var(image) / (std_dev + 1e-8) if std_dev > 0 else 0

# ==========================================
# 6. VISUALIZATION
# ==========================================
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1. Ground Truth")
    fig1, ax1 = plt.subplots(figsize=(5, 5))
    ax1.imshow(image, cmap='gray', vmin=0, vmax=1)
    ax1.axis('off')
    st.pyplot(fig1)

with col2:
    st.subheader(f"2. Sinogram (Noise: {noise_variance})")
    fig2, ax2 = plt.subplots(figsize=(5, 5))
    ax2.imshow(noisy_sinogram, cmap='gray', aspect='auto')
    ax2.set_xlabel("Detector Position")
    ax2.set_ylabel("Angle")
    st.pyplot(fig2)

with col3:
    st.subheader(f"3. {status_text}")
    fig3, ax3 = plt.subplots(figsize=(5, 5))
    ax3.imshow(final_image_clipped, cmap='gray', vmin=0, vmax=1)
    ax3.axis('off')
    st.pyplot(fig3)
    
    st.markdown("### Image Quality Metrics")
    st.metric(label="SSIM (Higher is better)", value=f"{score_ssim:.3f}")
    st.metric(label="PSNR (Higher is better)", value=f"{score_psnr:.2f} dB")
    st.metric(label="MSE (Lower is better)", value=f"{score_mse:.4f}")
    st.metric(label="Est. CNR", value=f"{score_cnr:.2f}")