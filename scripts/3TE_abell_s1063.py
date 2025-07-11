#!/usr/bin/env python3
"""
3TE_abell_s1063.py — Entropy lensing overlay for Abell S1063

Forked from 3TELenstronomy5.py
Adds: α-coupled 3T_E entropy tensor overlay
"""

import os
import cupy as cp
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits

from lenstronomy.Data.imaging_data import ImageData
from lenstronomy.Data.psf import PSF
from lenstronomy.LensModel.lens_model import LensModel
from lenstronomy.LightModel.light_model import LightModel
from lenstronomy.ImSim.image_model import ImageModel

# ======= CONFIG =======
DATA_PATH   = "data/abell_s1063_CROPPED.fits"
OUTPUT_PATH = "results/abell_s1063_LENS.png"
PIXEL_SCALE = 0.06     # arcsec/pixel
ALPHA_3TE   = 0.04
ENTROPY_GRAD_EST = 1e-3

# ======= ENTROPY POTENTIAL OVERLAY =======
def entropy_overlay_gpu(data_gpu, alpha, entropy_grad):
    grad = cp.gradient(data_gpu)
    grad_sum = cp.sum(cp.stack(grad), axis=0)
    return data_gpu + alpha * entropy_grad * grad_sum

# ======= MAIN FUNCTION =======
def run_entropy_overlay():
    print(f"Loading {DATA_PATH}")
    with fits.open(DATA_PATH) as hdul:
        data = hdul[0].data
        header = hdul[0].header
    ny, nx = data.shape
    print(f"Shape: {nx}×{ny} | Min: {data.min():.2f}, Max: {data.max():.2f}")

    kwargs_data = {
        'image_data': data,
        'transform_pix2angle': np.array([[PIXEL_SCALE, 0], [0, PIXEL_SCALE]]),
        'ra_at_xy_0': 0,
        'dec_at_xy_0': 0
    }
    data_class = ImageData(**kwargs_data)
    psf_class  = PSF(psf_type='GAUSSIAN', fwhm=0.05, pixel_size=PIXEL_SCALE)

    lens_model = LensModel(lens_model_list=['SIE', 'SHEAR'])
    lens_center_x = (nx / 2) * PIXEL_SCALE
    lens_center_y = (ny / 2) * PIXEL_SCALE
    kwargs_lens = [
        {'theta_E': 30.0, 'e1': 0.2, 'e2': -0.1, 'center_x': lens_center_x, 'center_y': lens_center_y},
        {'gamma1': 0.05, 'gamma2': 0.02}
    ]

    kwargs_source = [{
        'amp': 300, 'R_sersic': 0.3, 'n_sersic': 2.0,
        'e1': 0.0, 'e2': 0.0,
        'center_x': lens_center_x + 2.0,
        'center_y': lens_center_y - 1.0
    }]
    source_model = LightModel(light_model_list=['SERSIC_ELLIPSE'])

    imageModel = ImageModel(
        data_class=data_class,
        psf_class=psf_class,
        lens_model_class=lens_model,
        source_model_class=source_model,
        kwargs_numerics={"supersampling_factor": 1}
    )

    model_image = imageModel.image(kwargs_lens=kwargs_lens, kwargs_source=kwargs_source)

    # GPU entropy overlay
    data_gpu = cp.asarray(data)
    te_gpu = entropy_overlay_gpu(data_gpu, ALPHA_3TE, ENTROPY_GRAD_EST)
    te_cpu = cp.asnumpy(te_gpu)

    # Normalize overlays
    def norm(arr): return (arr - arr.min()) / (arr.max() - arr.min() + 1e-12)
    overlay = np.dstack((norm(te_cpu), norm(model_image), norm(data)))

    fig, axs = plt.subplots(1, 4, figsize=(16, 4))
    axs[0].imshow(norm(data), origin='lower', cmap='gray'); axs[0].set_title("Data"); axs[0].axis('off')
    axs[1].imshow(norm(model_image), origin='lower', cmap='gray'); axs[1].set_title("Model"); axs[1].axis('off')
    axs[2].imshow(norm(te_cpu), origin='lower', cmap='gray'); axs[2].set_title("3T_E Potential"); axs[2].axis('off')
    axs[3].imshow(overlay, origin='lower'); axs[3].set_title("Overlay (R=3T_E, G=Model, B=Data)"); axs[3].axis('off')
    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=200)
    print(f"Saved overlay to {OUTPUT_PATH}")

if __name__ == "__main__":
    run_entropy_overlay()
