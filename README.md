# ASTRA-Powered CT Simulator

An interactive Computed Tomography (CT) simulator built with Streamlit and the ASTRA Toolbox. This project investigates the effect of projection sampling density and noise on CT image reconstruction quality.

## Project Team

| Role | Member |
|---|---|
| Sampling | Heidi |
| Noising | Hagar |
| Denoising | Bassant |
| Contrast + 4th Metric (CNR) | Laila |
| Image Quality Metrics (SSIM, PSNR, MSE) | Fatma |

## Features

- Forward projection (Radon Transform) via ASTRA Toolbox
- Adjustable projection sampling density (up to the Crowther criterion limit)
- Simulated sinogram noise (Gaussian, models low-dose acquisition)
- FBP reconstruction with Ram-Lak filter
- Optional TV denoising correction
- Image quality metrics: SSIM, PSNR, MSE, CNR
- Upload custom images or use the built-in Shepp-Logan phantom

## Installation

This project requires the ASTRA Toolbox, which must be installed via conda:

```bash
conda create -n ct_simulator python=3.11
conda activate ct_simulator
conda install -c astra-toolbox -c conda-forge astra-toolbox streamlit numpy matplotlib pillow scikit-image
```

## Running the App

```bash
conda activate ct_simulator
streamlit run STREAMLIT_CT.py
```

## Physics Background

The simulator is based on the **Radon Transform**: for each projection angle θ, the X-ray beam integrates the object's attenuation coefficient along parallel lines. The resulting 2D data structure is called a **sinogram**.

Reconstruction uses **Filtered Back Projection (FBP)** with a Ram-Lak (ramp) filter, which corrects for the low-frequency overrepresentation inherent in naive back-projection.

The maximum number of projections is set by the **Crowther Criterion**:

```
min_projections = (π / 2) × N
```

For a 400×400 image, this gives ~630 projections.

## Sample Images

The `BrainCT.jpg` and `LungCT.jpeg` files are included as test inputs for the custom image uploader.
