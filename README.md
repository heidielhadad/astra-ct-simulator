# ASTRA-Powered CT Simulator

An interactive Computed Tomography (CT) simulator built with Streamlit and the ASTRA Toolbox. This project investigates the effect of projection sampling density and noise on CT image reconstruction quality.


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


## Sample Images

The `BrainCT.jpg` and `LungCT.jpeg` files are included as test inputs for the custom image uploader.
