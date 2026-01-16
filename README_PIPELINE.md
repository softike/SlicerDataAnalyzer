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
   --slicer-extra-arg=--qt-disable-translate --exit-after-run

python batch_stem_analysis.py \
   --image-root  /media/developer/Storage1/HFRStudy-RUN2/classif_SORT_04/ \
   --planning-root  /media/developer/Storage1/HFRStudy-RUN2/images/H002 \
   --stl-folder /media/developer/Storage1/HFRStudy-RUN2/Implants4EZplan \
   --slicer-extra-arg=--qt-disable-translate --exit-after-run

python batch_stem_analysis.py \
   --image-root  /media/developer/Storage1/HFRStudy-RUN2/classif_SORT_04/ \
   --planning-root  /media/developer/Storage1/HFRStudy-RUN2/images/H003 \
   --stl-folder /media/developer/Storage1/HFRStudy-RUN2/Implants4EZplan \
   --slicer-extra-arg=--qt-disable-translate --exit-after-run
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
