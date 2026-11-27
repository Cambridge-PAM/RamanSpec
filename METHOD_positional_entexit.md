# Method statement: entrance/exit Raman map comparison (`positional_entexit`)

## 1. Purpose

Compare Raman maps recorded at the entrance (Ent) and exit (Exit) of a sample
pair (e.g. TEP_Ent / TEP_Exit, MEP_Ent / MEP_Exit). Each pair is shown as one
square map split along its diagonal, together with a separate Exit − Ent
difference map. Peak-area and peak-ratio maps are produced.

## 2. Data

- Input: hyperspectral Raman maps exported as `.txt` files, one file per
  map. Each row is one spectrum point with columns X, Y (or R, Z), Raman shift
  (cm⁻¹) and intensity.
- Files are selected with `input.indices` and named with `input.rename`.
  Names must match those used in `entexit_pairs`.
- All files are loaded together in a single run so each pair can be matched.
  Each pixel is identified as `<name>_X<x>_Y<y>` (or `_R<r>_Z<z>`).

## 3. Configuration

```yaml
analysistype: 'positional_entexit'
entexit_pairs:               # [entrance, exit]; entrance = bottom-left triangle
  - ['TEP_Ent', 'TEP_Exit']
  - ['MEP_Ent', 'MEP_Exit']
```

Optional: `plotting.entexit_cmap` (default `viridis`) and
`plotting.entexit_diff_cmap` (default `RdBu_r`). The ratios to map are listed
under `ratios`, and the peak windows under `peaks.ranges`.

Run with `python scripts/run_analysis.py` (reads `config/config.yaml`).

## 4. Processing steps

Steps are applied to each pixel spectrum independently, in this order.

1. **Edge cropping** (if `processing.crop_edge_pixels.enabled`): the outer
   `pixels` rows and columns of each map are removed (2 in the publication
   config) to discard edge artefacts.
2. **Baseline correction** (if `processing.baseline`): asymmetrically
   reweighted penalised least squares (arPLS, `pybaselines`) with
   λ = 1×10⁶. The baseline is subtracted and negative values are set to zero.
3. **Normalisation** (if `processing.normalize`): each spectrum is divided by
   the sum of its baseline-corrected intensities (area normalisation), so
   spectra are comparable between pixels and maps.
4. **Smoothing** (if `processing.smoothing`): Savitzky–Golay filter (window 7,
   order 3). Disabled in the publication config.

## 5. Peak fitting

For each window in `peaks.ranges`, the processed spectrum within the window
bounds is fitted with a sum of Voigt profiles, one per listed peak, using
non-linear least squares (`scipy.optimize.curve_fit`, max 30,000 evaluations).

- Parameters per peak: amplitude, centre, σ (Gaussian width) and γ
  (Lorentzian width).
- Constraints: centre within ± `peaks.tolerance` (2 cm⁻¹) of the nominal
  position; 1 ≤ σ ≤ 20; 0.5 ≤ γ ≤ 15; amplitude ≥ 0.
- **Peak area** is the numerical integral (trapezoidal rule, 500 points) of
  the fitted Voigt profile across the window bounds.
- If a fit fails, has fewer than 10 points in the window, or the spectrum is
  empty, that peak's area is set to 0 for that pixel.

## 6. Ratio calculation

For each pair in `ratios`, ratio = PeakArea(peak 1) / PeakArea(peak 2) per
pixel. Fitted peaks are matched to the requested positions within
`peaks.tolerance`. A pixel is given a ratio of 0 when:

- the **raw** (unprocessed) spectrum's integrated intensity is below
  `peaks.intensity_threshold` (acts as a signal-quality filter);
- either peak is not found within tolerance;
- the denominator area is zero or non-finite; or
- the ratio exceeds 100 in magnitude.

Zeros therefore mean "no valid value", not a true ratio of zero.

## 7. Outputs

All outputs go to `outputs/<experiment>/`. File names are
`<experiment>__<ent>_vs_<exit>__<map>`, for example
`Raman__MEP_Ent_vs_MEP_Exit__ratio_597_over_530.png`.

| Output | Name suffix | Formats |
|---|---|---|
| Split ratio map | `ratio_<p1>_over_<p2>` | PNG, PDF, CSV |
| Ratio difference map | `ratio_<p1>_over_<p2>_difference` | PNG, PDF, CSV |
| Split peak-area map | `PeakArea_<peak>` | PNG, CSV |
| Peak-area difference map | `PeakArea_<peak>_difference` | PNG, CSV |

- **Split map:** bottom-left triangle = entrance map, top-right triangle =
  exit map. Both halves share one colormap and one colour scale (the common
  min/max of the pair, or `plotting.ratio_map_limits` for a configured ratio;
  otherwise `plotting.map_limits.ratio` is used when enabled).
- Configured `plotting.ratio_multipliers` scale matching sample ratios before
  ratio plots and maps are generated; unconfigured samples and ratios are
  unchanged.
- **Difference map:** Exit − Ent per pixel, on a symmetric diverging scale
  centred on zero. Only pixels present in both maps are used.
- **Figure style:** Arial, 22 pt. PDFs embed text as editable fonts (TrueType,
  `pdf.fonttype` 42); the map itself is raster.
- A metadata file (`<experiment>_<names>_metadata.txt`) records the run time,
  git commit and branch, whether there were uncommitted changes, and the full
  config used.

## 8. Assumptions and limitations

- Entrance and exit maps are assumed to cover the same pixel grid (same size
  and step). Pairs with different grid sizes are skipped with a warning.
- Maps are compared pixel by pixel by grid position, not registered or
  aligned. The axes show pixel index, not µm.
- 2D maps only; line scans (`positional2D`) are not supported in this mode.
- Intensity-threshold filtering uses the raw spectra, while fitting uses
  baseline-corrected, normalised spectra.
- Because spectra are area-normalised, peak areas are relative, not absolute.
- Ratio zeros (see section 6) appear in difference maps as artefacts where
  only one side is valid.
- Differences between maps are not tested statistically.
