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

## visualize stem and its HU heatmap

```shell
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H001/001-M-30/Mediplan3D/Slicer-exports/active_07/1.2.840.114356.244508491381643176892307433054188885352_stack_03_stem_local.vtp  --local-frame --show-gruen-zones --show-cut-plane --show-neck-point --opacity 0.5 --base-color 0.7,0.7,0.7 --side auto --show-axes --show-side-label --partitioned-gruen   --hu-table --export-hu-xml  --gruen-hu-zones top --show-bottom-point --show-offset

# with junction point
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H001/013-F-81/Mediplan3D/Slicer-exports/active_03/1.3.46.670589.33.1.63828549743236925000003.4985465118747613432_stem_local.vtp --local-frame --show-gruen-zones --show-cut-plane --show-neck-point --opacity 0.5 --base-color 0.7,0.7,0.7 --side auto --show-axes --show-side-label --partitioned-gruen   --hu-table --export-hu-xml  --show-bottom-point --show-offset --show-junction-point --show-junction-axes
```

## improve gruen zones partionong

```shell
# Corail right
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H001/013-F-81/Mediplan3D/Slicer-exports/active_03/1.3.46.670589.33.1.63828549743236925000003.4985465118747613432_stem_local.vtp --local-frame --show-cut-plane --show-neck-point --opacity 0.3 --base-color 0.7,0.7,0.7 --side auto  --show-side-label   --hu-table  --show-bottom-point --show-offset --show-junction-point --show-junction-axes  --convex-hull-opacity 0.8 --convex-hull-color 1,0.5,0 --convex-hull-mc --convex-hull-mc-spacing 0.5 --stem-mc --stem-mc-spacing 0.5  --show-envelope-gruen  --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --solid-zones   --show-axes  --cache-remesh 

# Corail left
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H001/009-F-83/Mediplan3D/Slicer-exports/active_03/1.2.840.113619.2.416.280121663397063837067761677027928059628_stack_03_stem_local.vtp --local-frame --show-cut-plane --show-neck-point --opacity 0.3 --base-color 0.7,0.7,0.7 --side auto  --show-side-label   --hu-table  --show-bottom-point --show-offset --show-junction-point --show-junction-axes  --convex-hull-opacity 0.8 --convex-hull-color 1,0.5,0 --convex-hull-mc --convex-hull-mc-spacing 0.5 --stem-mc --stem-mc-spacing 0.5  --show-envelope-gruen  --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --solid-zones   --show-axes  --cache-remesh 


# Mathys left - WRONG
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H002/001-M-30/Mediplan3D/Slicer-exports/active_07/1.2.840.114356.244508491381643176892307433054188885352_stack_03_stem_local.vtp --local-frame --show-cut-plane --show-neck-point --opacity 0.3 --base-color 0.7,0.7,0.7 --side auto  --show-side-label   --hu-table  --show-bottom-point --show-offset --show-junction-point --show-junction-axes  --convex-hull-opacity 0.8 --convex-hull-color 1,0.5,0 --convex-hull-mc --convex-hull-mc-spacing 0.5 --stem-mc --stem-mc-spacing 0.5  --show-envelope-gruen  --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --solid-zones   --show-axes  --cache-remesh 

# Mathys right
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H002/014-M-65/Mediplan3D/Slicer-exports/history_53/1.3.46.670589.33.1.63827950255467861600004.4736978582790340532_stem_local.vtp --local-frame --show-cut-plane --show-neck-point --opacity 0.3 --base-color 0.7,0.7,0.7 --side auto  --show-side-label   --hu-table  --show-bottom-point --show-offset --show-junction-point --show-junction-axes  --convex-hull-opacity 0.8 --convex-hull-color 1,0.5,0 --convex-hull-mc --convex-hull-mc-spacing 0.5 --stem-mc --stem-mc-spacing 0.5  --show-envelope-gruen  --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --solid-zones   --show-axes  --cache-remesh 

# Medacta AMISTEM right
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H003/002-F-36/Mediplan3D/Slicer-exports/history_120/1.2.840.114356.296552157972175411287775520654979109463_stack_03_stem_local.vtp --local-frame --show-cut-plane --show-neck-point --opacity 0.3 --base-color 0.7,0.7,0.7 --side auto  --show-side-label   --hu-table  --show-bottom-point --show-offset --show-junction-point --show-junction-axes  --convex-hull-opacity 0.8 --convex-hull-color 1,0.5,0 --convex-hull-mc --convex-hull-mc-spacing 0.5 --stem-mc --stem-mc-spacing 0.5  --envelope-z-bands 0.2,0.4,0.4 --show-envelope-gruen   --envelope-gruen-mode normal --solid-zones  --merge-zone-islands --merge-zone-min-points 1000 --show-axes

# Medacta AMISTEM left
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H003/002-F-36/Mediplan3D/Slicer-exports/history_89/1.2.840.114356.296552157972175411287775520654979109463_stack_03_stem_local.vtp --local-frame --show-cut-plane --show-neck-point --opacity 0.3 --base-color 0.7,0.7,0.7 --side auto  --show-side-label   --hu-table  --show-bottom-point --show-offset --show-junction-point --show-junction-axes  --convex-hull-opacity 0.8 --convex-hull-color 1,0.5,0 --convex-hull-mc --convex-hull-mc-spacing 0.5 --stem-mc --stem-mc-spacing 0.5  --show-envelope-gruen  --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --solid-zones  --merge-zone-islands --merge-zone-min-points 1000 --show-axes

# Medacta remove merging artefacts
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H003/002-F-36/Mediplan3D/Slicer-exports/history_89/1.2.840.114356.296552157972175411287775520654979109463_stack_03_stem_local.vtp --local-frame --show-cut-plane --show-neck-point --opacity 0.3 --base-color 0.7,0.7,0.7 --side auto  --show-side-label   --hu-table  --show-bottom-point --show-offset --show-junction-point --show-junction-axes  --convex-hull-opacity 0.8 --convex-hull-color 1,0.5,0 --convex-hull-mc --convex-hull-mc-spacing 0.5 --stem-mc --stem-mc-spacing 0.5  --show-envelope-gruen  --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --solid-zones   --show-axes  --cache-remesh --zone-only 12


# Actis right
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H003/001-M-30/Mediplan3D/Slicer-exports/history_126/1.2.840.114356.244508491381643176892307433054188885352_stack_03_stem_local.vtp --local-frame --show-cut-plane --show-neck-point --opacity 0.3 --base-color 0.7,0.7,0.7 --side auto  --show-side-label   --hu-table  --show-bottom-point --show-offset --show-junction-point --show-junction-axes  --convex-hull-opacity 0.8 --convex-hull-color 1,0.5,0 --convex-hull-mc --convex-hull-mc-spacing 0.5 --stem-mc --stem-mc-spacing 0.5  --show-envelope-gruen  --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --solid-zones  --merge-zone-islands --merge-zone-min-points 1000 --show-axes

```

## Visualize with remapping and no merging

```shell
# Corail right
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H001/013-F-81/Mediplan3D/Slicer-exports/active_03/1.3.46.670589.33.1.63828549743236925000003.4985465118747613432_stem_local.vtp --local-frame --show-cut-plane --show-neck-point --opacity 0.3 --base-color 0.7,0.7,0.7 --side auto  --show-side-label   --hu-table  --show-bottom-point --show-offset --show-junction-point --show-junction-axes  --convex-hull-opacity 0.8 --convex-hull-color 1,0.5,0 --convex-hull-mc --convex-hull-mc-spacing 0.5 --stem-mc --stem-mc-spacing 0.5 --solid-zones   --show-axes  --cache-remesh --show-envelope-gruen  --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --gruen-remapped --zone-only 1

# Corail left
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H001/009-F-83/Mediplan3D/Slicer-exports/active_03/1.2.840.113619.2.416.280121663397063837067761677027928059628_stack_03_stem_local.vtp --local-frame --show-cut-plane --show-neck-point --opacity 0.3 --base-color 0.7,0.7,0.7 --side auto  --show-side-label   --hu-table  --show-bottom-point --show-offset --show-junction-point --show-junction-axes  --convex-hull-opacity 0.8 --convex-hull-color 1,0.5,0 --convex-hull-mc --convex-hull-mc-spacing 0.5 --stem-mc --stem-mc-spacing 0.5 --solid-zones   --show-axes  --cache-remesh --show-envelope-gruen  --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --gruen-remapped --zone-only 1


# Mathys left
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H002/001-M-30/Mediplan3D/Slicer-exports/active_07/1.2.840.114356.244508491381643176892307433054188885352_stack_03_stem_local.vtp --local-frame --show-cut-plane --show-neck-point --opacity 0.3 --base-color 0.7,0.7,0.7 --side auto  --show-side-label   --hu-table  --show-bottom-point --show-offset --show-junction-point --show-junction-axes  --convex-hull-opacity 0.8 --convex-hull-color 1,0.5,0 --convex-hull-mc --convex-hull-mc-spacing 0.5 --stem-mc --stem-mc-spacing 0.5 --solid-zones   --show-axes  --cache-remesh --show-envelope-gruen  --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --gruen-remapped --zone-only 1


# Mathys right
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H002/014-M-65/Mediplan3D/Slicer-exports/history_53/1.3.46.670589.33.1.63827950255467861600004.4736978582790340532_stem_local.vtp --local-frame --show-cut-plane --show-neck-point --opacity 0.3 --base-color 0.7,0.7,0.7 --side auto  --show-side-label   --hu-table  --show-bottom-point --show-offset --show-junction-point --show-junction-axes  --convex-hull-opacity 0.8 --convex-hull-color 1,0.5,0 --convex-hull-mc --convex-hull-mc-spacing 0.5 --stem-mc --stem-mc-spacing 0.5 --solid-zones   --show-axes  --cache-remesh --show-envelope-gruen  --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --gruen-remapped --zone-only 1


# Medacta AMISTEM right
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H003/002-F-36/Mediplan3D/Slicer-exports/history_120/1.2.840.114356.296552157972175411287775520654979109463_stack_03_stem_local.vtp --local-frame --show-cut-plane --show-neck-point --opacity 0.3 --base-color 0.7,0.7,0.7 --side auto  --show-side-label   --hu-table  --show-bottom-point --show-offset --show-junction-point --show-junction-axes  --convex-hull-opacity 0.8 --convex-hull-color 1,0.5,0 --convex-hull-mc --convex-hull-mc-spacing 0.5 --stem-mc --stem-mc-spacing 0.5 --solid-zones   --show-axes  --cache-remesh --show-envelope-gruen  --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --gruen-remapped --zone-only 1

# Medacta AMISTEM left
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H003/002-F-36/Mediplan3D/Slicer-exports/history_89/1.2.840.114356.296552157972175411287775520654979109463_stack_03_stem_local.vtp --local-frame --show-cut-plane --show-neck-point --opacity 0.3 --base-color 0.7,0.7,0.7 --side auto  --show-side-label   --hu-table  --show-bottom-point --show-offset --show-junction-point --show-junction-axes  --convex-hull-opacity 0.8 --convex-hull-color 1,0.5,0 --convex-hull-mc --convex-hull-mc-spacing 0.5 --stem-mc --stem-mc-spacing 0.5 --solid-zones   --show-axes  --cache-remesh --show-envelope-gruen  --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --gruen-remapped --zone-only 1

# Actis right
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H003/001-M-30/Mediplan3D/Slicer-exports/history_126/1.2.840.114356.244508491381643176892307433054188885352_stack_03_stem_local.vtp --local-frame --show-cut-plane --show-neck-point --opacity 0.3 --base-color 0.7,0.7,0.7 --side auto  --show-side-label   --hu-table  --show-bottom-point --show-offset --show-junction-point --show-junction-axes  --convex-hull-opacity 0.8 --convex-hull-color 1,0.5,0 --convex-hull-mc --convex-hull-mc-spacing 0.5 --stem-mc --stem-mc-spacing 0.5 --solid-zones   --show-axes  --cache-remesh --show-envelope-gruen  --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --gruen-remapped --zone-only 1

```

## Minimize the options to get still Gruen zones

```shell
# this one works well
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H001/013-F-81/Mediplan3D/Slicer-exports/active_03/1.3.46.670589.33.1.63828549743236925000003.4985465118747613432_stem_local.vtp --local-frame --show-cut-plane --opacity 0.3 --base-color 0.7,0.7,0.7 --side auto  --show-side-label   --hu-table  --stem-mc --stem-mc-spacing 0.5 --solid-zones   --show-axes  --cache-remesh --show-envelope-gruen  --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --gruen-remapped --zone-only 1
```

## Add option to see HU per zone

```shell
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H001/013-F-81/Mediplan3D/Slicer-exports/active_03/1.3.46.670589.33.1.63828549743236925000003.4985465118747613432_stem_local.vtp --local-frame --show-cut-plane --opacity 0.3 --base-color 0.7,0.7,0.7 --side auto  --show-side-label   --hu-table  --stem-mc --stem-mc-spacing 0.5 --solid-zones   --show-axes  --cache-remesh --show-envelope-gruen  --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --envelope-hu --gruen-remapped --zone-only 1

# to just see the stem with HU on the whole body under the cut plane
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H001/013-F-81/Mediplan3D/Slicer-exports/active_03/1.3.46.670589.33.1.63828549743236925000003.4985465118747613432_stem_local.vtp --local-frame --show-cut-plane --opacity 1 --base-color 0.7,0.7,0.7 --side auto  --show-side-label   --hu-table  --stem-mc --stem-mc-spacing 0.5 --solid-zones   --show-axes  --cache-remesh
```

## 2 viewport visualization

```shell
 python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H001/013-F-81/Mediplan3D/Slicer-exports/active_03/1.3.46.670589.33.1.63828549743236925000003.4985465118747613432_stem_local.vtp --local-frame --show-cut-plane --opacity 1 --base-color 0.7,0.7,0.7 --side auto  --show-side-label  --stem-mc --stem-mc-spacing 0.5  --show-axes  --cache-remesh --show-envelope-gruen  --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal  --gruen-remapped --zone-only 14 --envelope-hu-viewports --opacity 1
```

## 2 viewport with stable zones only

```shell
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H001/013-F-81/Mediplan3D/Slicer-exports/active_03/1.3.46.670589.33.1.63828549743236925000003.4985465118747613432_stem_local.vtp --local-frame --show-cut-plane --opacity 1 --base-color 0.7,0.7,0.7 --side auto  --show-side-label  --stem-mc --stem-mc-spacing 0.5  --show-axes  --cache-remesh --show-envelope-gruen  --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal  --gruen-remapped --envelope-hu-viewports --opacity 1 --envelope-hu-stable 
```

## 2 viewport with cortical zones only

```shell
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H001/013-F-81/Mediplan3D/Slicer-exports/active_03/1.3.46.670589.33.1.63828549743236925000003.4985465118747613432_stem_local.vtp --local-frame --show-cut-plane --opacity 1 --base-color 0.7,0.7,0.7 --side auto  --show-side-label  --stem-mc --stem-mc-spacing 0.5  --show-axes  --cache-remesh --show-envelope-gruen  --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal  --gruen-remapped --envelope-hu-viewports --opacity 1 --envelope-hu-cortical 
```

## remesh with implicit modelling

```shell
python view_vtp.py --batch-remesh-input /media/developer/Storage1/HFRStudy-RUN2/Implants4EZplan/ --batch-remesh-output /media/developer/Storage1/HFRStudy-RUN2/Implants4EZplanv3/ --pre-mc-fill-holes --normal-ray-filter --normal-ray-auto-orient --normal-ray-eps 0.1  --remesh-iso --remesh-target 30000  --stem-mc --stem-mc-spacing 0.5   --batch-remesh-verbose --batch-export-normal-ray
```

## remesh with pyacvd

```shell
python view_vtp.py --batch-remesh-input /media/developer/Storage1/HFRStudy-RUN2/Implants4EZplan/ --batch-remesh-output /media/developer/Storage1/HFRStudy-RUN2/Implants4EZplanv3/   --remesh-iso --remesh-target-factor 2.0  --batch-remesh-verbose 
```

## using the remeshed surface directly

```shell
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H001/013-F-81/Mediplan3D/Slicer-exports/active_03/1.3.46.670589.33.1.63828549743236925000003.4985465118747613432_stem_local.vtp --local-frame --show-cut-plane --opacity 1 --base-color 0.7,0.7,0.7 --side auto  --show-side-label --show-axes --show-envelope-gruen --gruen-hu-remesh-input --envelope-gruen-input --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --gruen-remapped --zone-only 1 --envelope-hu-viewports


# Corail right
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H001/013-F-81/Mediplan3D/Slicer-exports/active_03/1.3.46.670589.33.1.63828549743236925000003.4985465118747613432_stem_local.vtp --local-frame --show-cut-plane --opacity 1 --base-color 0.7,0.7,0.7 --side auto  --show-side-label --show-axes --show-envelope-gruen --gruen-hu-remesh-input --envelope-gruen-input --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --gruen-remapped --zone-only 1 --envelope-hu-viewports

# Corail left
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H001/009-F-83/Mediplan3D/Slicer-exports/active_03/1.2.840.113619.2.416.280121663397063837067761677027928059628_stack_03_stem_local.vtp --local-frame --show-cut-plane --opacity 1 --base-color 0.7,0.7,0.7 --side auto  --show-side-label --show-axes --show-envelope-gruen --gruen-hu-remesh-input --envelope-gruen-input --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --gruen-remapped --zone-only 1 --envelope-hu-viewports


# Mathys left
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H002/001-M-30/Mediplan3D/Slicer-exports/active_07/1.2.840.114356.244508491381643176892307433054188885352_stack_03_stem_local.vtp --local-frame --show-cut-plane --opacity 1 --base-color 0.7,0.7,0.7 --side auto  --show-side-label --show-axes --show-envelope-gruen --gruen-hu-remesh-input --envelope-gruen-input --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --gruen-remapped --zone-only 1 --envelope-hu-viewports


# Mathys right
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H002/014-M-65/Mediplan3D/Slicer-exports/history_53/1.3.46.670589.33.1.63827950255467861600004.4736978582790340532_stem_local.vtp --local-frame --show-cut-plane --opacity 1 --base-color 0.7,0.7,0.7 --side auto  --show-side-label --show-axes --show-envelope-gruen --gruen-hu-remesh-input --envelope-gruen-input --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --gruen-remapped --zone-only 1 --envelope-hu-viewports


# Medacta AMISTEM right
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H003/002-F-36/Mediplan3D/Slicer-exports/history_120/1.2.840.114356.296552157972175411287775520654979109463_stack_03_stem_local.vtp --local-frame --show-cut-plane --opacity 1 --base-color 0.7,0.7,0.7 --side auto  --show-side-label --show-axes --show-envelope-gruen --gruen-hu-remesh-input --envelope-gruen-input --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --gruen-remapped --zone-only 1 --envelope-hu-viewports

# Medacta AMISTEM left
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H003/002-F-36/Mediplan3D/Slicer-exports/history_89/1.2.840.114356.296552157972175411287775520654979109463_stack_03_stem_local.vtp --local-frame --show-cut-plane --opacity 1 --base-color 0.7,0.7,0.7 --side auto  --show-side-label --show-axes --show-envelope-gruen --gruen-hu-remesh-input --envelope-gruen-input --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --gruen-remapped --zone-only 1 --envelope-hu-viewports

# Actis right
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H003/001-M-30/Mediplan3D/Slicer-exports/history_126/1.2.840.114356.244508491381643176892307433054188885352_stack_03_stem_local.vtp --local-frame --show-cut-plane --opacity 1 --base-color 0.7,0.7,0.7 --side auto  --show-side-label --show-axes --show-envelope-gruen --gruen-hu-remesh-input --envelope-gruen-input --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --gruen-remapped --zone-only 1 --envelope-hu-viewports
```

## Do the Gruen analysis

```shell
python batch_export_gruen_tables.py  --root /media/developer/Storage1/HFRStudy-RUN2/images/ --recursive --side auto --envelope-gruen --envelope-gruen-mode normal --use-input-remesh --envelope-z-bands 0.2,0.4,0.4 --gruen-remapped --gruen-hu-remesh --gruen-bottom-sphere-radius 10 --verbose
```

## Get stem with hu under the cut plane

```shell
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H001/013-F-81/Mediplan3D/Slicer-exports/active_03/1.3.46.670589.33.1.63828549743236925000003.4985465118747613432_stem_local.vtp --local-frame --show-cut-plane --opacity 0.3 --base-color 0.7,0.7,0.7 --side auto  --show-side-label --show-axes  --gruen-hu-remesh-input --gruen-remapped  --solid-zones 
```

## Show all gruen zones

```shell
# Medacta left
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H003/002-F-36/Mediplan3D/Slicer-exports/history_89/1.2.840.114356.296552157972175411287775520654979109463_stack_03_stem_local.vtp --local-frame --show-cut-plane --opacity 1 --base-color 0.7,0.7,0.7 --side auto  --show-side-label --show-axes --show-envelope-gruen --gruen-hu-remesh-input --envelope-gruen-input --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --gruen-remapped --preserve-exports

# Corail right
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H001/013-F-81/Mediplan3D/Slicer-exports/active_03/1.3.46.670589.33.1.63828549743236925000003.4985465118747613432_stem_local.vtp --local-frame --show-cut-plane --opacity 1 --base-color 0.7,0.7,0.7 --side auto  --show-side-label --show-axes --show-envelope-gruen --gruen-hu-remesh-input --envelope-gruen-input --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --gruen-remapped --preserve-exports

# Corail left
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H001/009-F-83/Mediplan3D/Slicer-exports/active_03/1.2.840.113619.2.416.280121663397063837067761677027928059628_stack_03_stem_local.vtp --local-frame --show-cut-plane --opacity 1 --base-color 0.7,0.7,0.7 --side auto  --show-side-label --show-axes --show-envelope-gruen --gruen-hu-remesh-input --envelope-gruen-input --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --gruen-remapped --preserve-exports

# Mathys right
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H002/014-M-65/Mediplan3D/Slicer-exports/history_53/1.3.46.670589.33.1.63827950255467861600004.4736978582790340532_stem_local.vtp --local-frame --show-cut-plane --opacity 1 --base-color 0.7,0.7,0.7 --side auto  --show-side-label --show-axes --show-envelope-gruen --gruen-hu-remesh-input --envelope-gruen-input --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --gruen-remapped --preserve-exports

# Mathys left
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H002/001-M-30/Mediplan3D/Slicer-exports/active_07/1.2.840.114356.244508491381643176892307433054188885352_stack_03_stem_local.vtp --local-frame --show-cut-plane --opacity 1 --base-color 0.7,0.7,0.7 --side auto  --show-side-label --show-axes --show-envelope-gruen --gruen-hu-remesh-input --envelope-gruen-input --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --gruen-remapped --preserve-exports

# Medacta AMISTEM right
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H003/002-F-36/Mediplan3D/Slicer-exports/history_120/1.2.840.114356.296552157972175411287775520654979109463_stack_03_stem_local.vtp --local-frame --show-cut-plane --opacity 1 --base-color 0.7,0.7,0.7 --side auto  --show-side-label --show-axes --show-envelope-gruen --gruen-hu-remesh-input --envelope-gruen-input --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --gruen-remapped --preserve-exports

# Medacta AMISTEM left
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H003/002-F-36/Mediplan3D/Slicer-exports/history_89/1.2.840.114356.296552157972175411287775520654979109463_stack_03_stem_local.vtp --local-frame --show-cut-plane --opacity 1 --base-color 0.7,0.7,0.7 --side auto  --show-side-label --show-axes --show-envelope-gruen --gruen-hu-remesh-input --envelope-gruen-input --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --gruen-remapped --preserve-exports

# Actis right
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN2/images/H003/001-M-30/Mediplan3D/Slicer-exports/history_126/1.2.840.114356.244508491381643176892307433054188885352_stack_03_stem_local.vtp --local-frame --show-cut-plane --opacity 1 --base-color 0.7,0.7,0.7 --side auto  --show-side-label --show-axes --show-envelope-gruen --gruen-hu-remesh-input --envelope-gruen-input --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --gruen-remapped --preserve-exports

# Ecofit Left
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN3/images/H003/002-F-36/Mediplan3D/Slicer-exports/active_21/1.2.840.114356.296552157972175411287775520654979109463_stack_03_stem_local.vtp --local-frame --show-cut-plane --opacity 1 --base-color 0.7,0.7,0.7 --side auto  --show-side-label --show-axes --show-envelope-gruen --gruen-hu-remesh-input --envelope-gruen-input --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --gruen-remapped --preserve-exports

# Ecofit Right
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN3/images/H003/001-M-30/Mediplan3D/Slicer-exports/active_16/1.2.840.114356.244508491381643176892307433054188885352_stack_03_stem_local.vtp --local-frame --show-cut-plane --opacity 1 --base-color 0.7,0.7,0.7 --side auto  --show-side-label --show-axes --show-envelope-gruen --gruen-hu-remesh-input --envelope-gruen-input --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --gruen-remapped --preserve-exports

# Fit Right
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN3/images/H002/017-F-81/Mediplan3D/Slicer-exports/history_45/1.2.840.113619.2.416.271784315531619414068681057291616558552_stem_local.vtp  --local-frame --show-cut-plane --opacity 1 --base-color 0.7,0.7,0.7 --side auto  --show-side-label --show-axes --show-envelope-gruen --gruen-hu-remesh-input --envelope-gruen-input --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --gruen-remapped --preserve-exports


# FIT left
python view_vtp.py /media/developer/Storage1/HFRStudy-RUN3/images/H002/019-F-54/Mediplan3D/Slicer-exports/history_56/1.2.840.113619.2.416.81709775698183917206599124984821901551_stem_local.vtp --local-frame --show-cut-plane --opacity 1 --base-color 0.7,0.7,0.7 --side auto  --show-side-label --show-axes --show-envelope-gruen --gruen-hu-remesh-input --envelope-gruen-input --envelope-z-bands 0.2,0.4,0.4 --envelope-gruen-mode normal --gruen-remapped --preserve-exports


```

## Test a specific case in Slicer

```shell
python batch_stem_analysis.py \
   --image-root  /media/developer/Storage1/HFRStudy-RUN2/classif_SORT_04/ \
   --planning-root  /media/developer/Storage1/HFRStudy-RUN3/images/H001 \
   --stl-folder /media/developer/Storage1/HFRStudy-RUN2/Implants4EZplan \
   --slicer-extra-arg=--qt-disable-translate --show-cut-plane --show-neck-point --scalar-below-cut-plane --export-local-stem --cortical-unbounded --case 001-M-30 --config-index 34   --preserve-exports  --export-scene 

python batch_stem_analysis.py \
   --image-root  /media/developer/Storage1/HFRStudy-RUN2/classif_SORT_04/ \
   --planning-root  /media/developer/Storage1/HFRStudy-RUN3/images/H001 \
   --stl-folder /media/developer/Storage1/HFRStudy-RUN2/Implants4EZplan \
   --slicer-extra-arg=--qt-disable-translate --show-cut-plane --show-neck-point --scalar-below-cut-plane --export-local-stem --cortical-unbounded --case 001-M-30 --config-index 34   --preserve-exports  --export-scene 

```

## Full process

```shell
python batchCompareStudies.py --base_path /media/developer/Storage1/HFRStudy-RUN2/images --output batch_report_RUN2 --output-path ./CurrentReports/RUN2_4/  --excel 

python batch_stem_analysis.py \
   --image-root  /media/developer/Storage1/HFRStudy-RUN2/classif_SORT_04/ \
   --planning-root  /media/developer/Storage1/HFRStudy-RUN3/images/H001 \
   --stl-folder /media/developer/Storage1/HFRStudy-RUN2/Implants4EZplan \
   --slicer-extra-arg=--qt-disable-translate --show-cut-plane --show-neck-point --scalar-below-cut-plane --export-local-stem --cortical-unbounded --exit-after-run

python batch_stem_analysis.py \
   --image-root  /media/developer/Storage1/HFRStudy-RUN2/classif_SORT_04/ \
   --planning-root  /media/developer/Storage1/HFRStudy-RUN3/images/H002 \
   --stl-folder /media/developer/Storage1/HFRStudy-RUN2/Implants4EZplan \
   --slicer-extra-arg=--qt-disable-translate --show-cut-plane --show-neck-point --scalar-below-cut-plane --export-local-stem --cortical-unbounded --exit-after-run

python batch_stem_analysis.py \
   --image-root  /media/developer/Storage1/HFRStudy-RUN2/classif_SORT_04/ \
   --planning-root  /media/developer/Storage1/HFRStudy-RUN3/images/H003 \
   --stl-folder /media/developer/Storage1/HFRStudy-RUN2/Implants4EZplan \
   --slicer-extra-arg=--qt-disable-translate --show-cut-plane --show-neck-point --scalar-below-cut-plane --export-local-stem --cortical-unbounded --exit-after-run

python batch_export_gruen_tables.py  --root /media/developer/Storage1/HFRStudy-RUN2/images/ --recursive --side auto --envelope-gruen --envelope-gruen-mode normal --use-input-remesh --envelope-z-bands 0.2,0.4,0.4 --gruen-remapped --gruen-hu-remesh --cortical-unbounded --gruen-bottom-sphere-radius 10 --verbose

python export_stem_metrics_excel.py --root /media/developer/Storage1/HFRStudy-RUN2/images/ --output /home/developer/Projects/Code/SlicerDataAnalyzer/CurrentReports/RUN2_8/stem_metrics_RUN2_CORTICAL2000.xlsx
```

