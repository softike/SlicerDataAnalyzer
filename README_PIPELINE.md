# How to extract data from EZplan planning reports

## From EZplan 

```shell
python batchCompareStudies.py --base_path /media/developer/Storage1/HFRStudy-RUN2/images --output batch_report_RUN2 --output-path ./CurrentReports/RUN2_4/  --excel 
```

## From Slicer for each participants

```shell
python batch_stem_analysis.py \
   --image-root  /media/developer/Storage1/HFRStudy-RUN2/classif_SORT_04/ \
   --planning-root  /media/developer/Storage1/HFRStudy-RUN2/images/H001 \
   --stl-folder /media/developer/Storage1/HFRStudy-RUN2/Implants4EZplan \
   --slicer-extra-arg=--qt-disable-translate --show-cut-plane --show-neck-point --scalar-below-cut-plane --export-local-stem --exit-after-run

python batch_stem_analysis.py \
   --image-root  /media/developer/Storage1/HFRStudy-RUN2/classif_SORT_04/ \
   --planning-root  /media/developer/Storage1/HFRStudy-RUN2/images/H002 \
   --stl-folder /media/developer/Storage1/HFRStudy-RUN2/Implants4EZplan \
   --slicer-extra-arg=--qt-disable-translate --show-cut-plane --show-neck-point --scalar-below-cut-plane --export-local-stem --exit-after-run

python batch_stem_analysis.py \
   --image-root  /media/developer/Storage1/HFRStudy-RUN2/classif_SORT_04/ \
   --planning-root  /media/developer/Storage1/HFRStudy-RUN2/images/H003 \
   --stl-folder /media/developer/Storage1/HFRStudy-RUN2/Implants4EZplan \
   --slicer-extra-arg=--qt-disable-translate --show-cut-plane --show-neck-point --scalar-below-cut-plane --export-local-stem --exit-after-run
```

> Tip: when a `seedplan.xml` contains multiple femoral stem configurations (active plus histories), the batch driver now processes every configuration automatically. Each configuration gets its own subfolder under the case’s `Slicer-exports/` directory with screenshots, VTP, and metrics XML, so you can review every contact analysis without relaunching Slicer.

## For test to see how the stem is inserted, do it for each participants, H001 is for Corail, H002 ..., H003 for the Amistem.

```shell
# Corail
python ./load_nifti_and_stem.py --nifti /media/developer/Storage1/HFRStudy-RUN2/classif_SORT_04/006-M-63/Dataset/1.2.840.113619.2.416.323108426829918732464075286489137100165/stacks/stack_03/nifti/1.2.840.113619.2.416.323108426829918732464075286489137100165_stack_03.nii.gz  --seedplan /media/developer/Storage1/HFRStudy-RUN2/images/H001/006-M-63/Mediplan3D/seedplan.xml --stl-folder /media/developer/Storage1/HFRStudy-RUN2/Implants4EZplan  --no-splash --pre-rotate-z-180 --post-rotate-z-180

# Optimys
python ./load_nifti_and_stem.py --nifti /media/developer/Storage1/HFRStudy-RUN2/classif_SORT_04/006-M-63/Dataset/1.2.840.113619.2.416.323108426829918732464075286489137100165/stacks/stack_03/nifti/1.2.840.113619.2.416.323108426829918732464075286489137100165_stack_03.nii.gz  --seedplan /media/developer/Storage1/HFRStudy-RUN2/images/H002/006-M-63/Mediplan3D/seedplan.xml --stl-folder /media/developer/Storage1/HFRStudy-RUN2/Implants4EZplan  --no-splash --pre-rotate-z-180 --post-rotate-z-180

# Amistem
python ./load_nifti_and_stem.py --nifti /media/developer/Storage1/HFRStudy-RUN2/classif_SORT_04/006-M-63/Dataset/1.2.840.113619.2.416.323108426829918732464075286489137100165/stacks/stack_03/nifti/1.2.840.113619.2.416.323108426829918732464075286489137100165_stack_03.nii.gz  --seedplan /media/developer/Storage1/HFRStudy-RUN2/images/H003/006-M-63/Mediplan3D/seedplan.xml --stl-folder /media/developer/Storage1/HFRStudy-RUN2/Implants4EZplan  --no-splash --pre-rotate-z-180 --post-rotate-z-180
```

## Extract all metrics

```shell
python export_stem_metrics_excel.py --root /media/developer/Storage1/HFRStudy-RUN2/images/ --output /home/developer/Projects/Code/SlicerDataAnalyzer/CurrentReports/RUN2_4/stem_metrics_RUN2.xlsx
```

The resulting workbook lists every stem configuration (label/source/index plus the original `hipImplantConfig` name) on the `Cases` sheet and summarizes both unique cases and total configurations per planner on the `Users` sheet.

## View cut planes

```shell
python view_implant.py STEM_STD_6 /media/developer/Storage1/HFRStudy-RUN2/Implants4EZplan \
  --manufacturer johnson-actis \
  --plane-size 80 \
  --verbose

python view_implant.py STEM_KHO_A_135_4 /media/developer/Storage1/HFRStudy-RUN2/Implants4EZplan \
  --manufacturer johnson-corail \
  --plane-size 70 \
  --verbose

python view_implant.py STEM_STD_1 /media/developer/Storage1/HFRStudy-RUN2/Implants4EZplan \
  --manufacturer mathys \
  --plane-size 80 \
  --verbose

python view_implant.py STEM_STD_2 /media/developer/Storage1/HFRStudy-RUN2/Implants4EZplan \
  --manufacturer medacta \
  --plane-size 80 \
  --verbose

# show other annotation
python view_implant.py STEM_KHO_A_135_4 /media/developer/Storage1/HFRStudy-RUN2/Implants4EZplan \
  --manufacturer johnson-corail \
  --show-head --show-offset --offset-head HEAD_P4 \
  --show-all-offsets --stem-opacity 0.35

# show res_01, res_02 or tpr_01


# show jonction

python view_implant.py STEM_KHO_A_135_4 /media/developer/Storage1/HFRStudy-RUN2/Implants4EZplan \
  --manufacturer johnson-corail \
  --show-tip-point --show-bottom-point --show-axis-junction --show-shaft-axis \
  --show-cut-plane-intersection --show-cut-plane-contour --show-anatomical-plane \
  --show-axes-reference \
  --plane-size 70 --stem-opacity 0.35

python view_implant.py STEM_KHO_A_135_4 /media/developer/Storage1/HFRStudy-RUN2/Implants4EZplan \
  --manufacturer johnson-corail \
  --show-axis-junction --show-neck-axis --plane-size 70 --stem-opacity 0.35

# Mathys example (auto Z-flip and CCD verification)
python view_implant.py STEM_STD_2 /media/developer/Storage1/HFRStudy-RUN2/Implants4EZplan \
  --manufacturer mathys \
  --show-tip-point --show-bottom-point \
  --show-axis-junction --show-neck-axis --verify-ccd-angle --plane-size 70 --stem-opacity 0.35

python view_implant.py STEM_STD_2 /media/developer/Storage1/HFRStudy-RUN2/Implants4EZplan \
  --manufacturer medacta \
  --show-tip-point --show-bottom-point --show-axis-junction --show-neck-axis \
  --show-cut-plane-intersection --show-cut-plane-contour --show-anatomical-plane \
  --show-axes-reference \
  --plane-size 70 --stem-opacity 0.35

python view_implant.py STEM_STD_2 /media/developer/Storage1/HFRStudy-RUN2/Implants4EZplan \
  --manufacturer mathys \
    --show-neck-axis --plane-size 70  --stem-opacity 0.35 --show-tip-point --show-bottom-point --show-cut-plane-intersection --show-cut-plane-contour --show-anatomical-plane --show-axes

```

> Rotation tip: `view_implant.py` now reuses the batch auto-rotation heuristics. Leave `--rotation-mode` at its default `auto` for Mathys/Medacta/Johnson stems, or force a behavior with `--rotation-mode mathys|medacta|johnson|none`. Manual overrides such as `--pre-rotate-z-180` / `--post-rotate-z-180` stack on top of the auto detection when a brand needs a specific flip. Use `--show-tip-point` / `--show-bottom-point` to highlight the superior/inferior extremes detected from the STL principal axis; the viewer automatically draws the stem axis from the bottom extremity to the neck/stem junction whenever those analytics are requested. Mathys stems additionally receive the axis remap `X=-X, Y=-Z, Z=-Y`, Medacta stems use `X=-Y, Y=+X, Z=Z`, and Johnson Corail stems apply `X=-X, Y=-Y, Z=Z`, so each local reference aligns with the standard XYZ orientation before visualization; Johnson Actis continues rendering in its native frame. Add `--show-axis-frames` to display the initial implant frame (pre-brand transform) when you need to double-check orientation references, or pass `--native-orientation` to bypass every auto/manufacturer transform and inspect the STL exactly as it was saved. The viewer camera now defaults to `+Z` pointing up, `+Y` pointing into the screen, and `+X` toward the right edge so every stem loads with a consistent frame of reference.

> Add `--show-cut-plane-intersection` to compute and visualize the upper and lower cut/stem contacts that lie on both the rotated cut plane and the anatomical plane defined by the neck, head, and STL-derived tip—the viewer now explicitly intersects the cut contour with that anatomical plane, and only falls back to the contour extremes when the plane cannot be formed. Pair it with `--show-cut-plane-contour` to display the entire cut/stem intersection contour so you can confirm the contacts are centered, add `--show-anatomical-plane` to render that head/neck/tip plane directly in the scene, and include `--show-axes-reference` whenever you need a visible XYZ orientation cue.
