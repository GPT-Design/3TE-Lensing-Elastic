#!/usr/bin/env python3
"""
3TE_jet_ngc7385.py — Elastic shear overlay test on jet–cloud impact zone

Target: NGC 7385 (Chandra FITS image)
Assumes brightness acts as deformation proxy φ
"""

import os
import numpy as np
import cupy as cp
import matplotlib.pyplot as plt
from astropy.io import fits

from models.elastic_tensor import elastic_tensor_Tmunu

# ======= CONFIG =======
DATA_PATH   = "data/ngc7385_xray.fits"
OUTPUT_PATH = "results/ngc7385_elastic_overlay.png"
G_ELASTIC   = 1e-9   # Pa

# ======= LOAD IMAGE =======
with fits.open(DATA_PATH) as hdul:
    data = hdul[0].data.astype(np.float32)
    header = hdul[0].header
ny, nx = data.shape
print(f"NGC 7385 image loaded: {nx}×{ny}")

# ======= DEFINE φ FIELD =======
# Use image brightness as proxy for φ^I fields
# Here: assume 2 pseudo-fields φ^1 = X-gradient, φ^2 = Y-gradient
phi1 = np.gradient(data, axis=1)
phi2 = np.gradient(data, axis=0)

# ======= ELASTIC TENSOR OVERLAY =======
T_elastic = elastic_tensor_Tmunu([phi1, phi2], shear_modulus=G_ELASTIC)
elastic_overlay = T_elastic[0] + T_elastic[1]  # Approximate trace for now

# Normalize for overlay
def norm(x): return (x - np.min(x)) / (np.max(x) - np.min(x) + 1e-12)
elastic_norm = norm(elastic_overlay)
data_norm = norm(data)

# ======= RGB COMPOSITE =======
overlay_rgb = np.dstack((elastic_norm, 0.5 * data_norm, data_norm))

# ======= PLOT =======
fig, axs = plt.subplots(1, 3, figsize=(15, 4))
axs[0].imshow(data_norm, cmap='gray', origin='lower'); axs[0].set_title("X-ray Data")
axs[1].imshow(elastic_norm, cmap='plasma', origin='lower'); axs[1].set_title("Elastic Overlay")
axs[2].imshow(overlay_rgb, origin='lower'); axs[2].set_title("R=Elastic, G=Data, B=Data")
for ax in axs: ax.axis('off')
plt.tight_layout()
plt.savefig(OUTPUT_PATH, dpi=200)
print(f"Elastic overlay saved: {OUTPUT_PATH}")

 
 
