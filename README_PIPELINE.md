# How to extract data from EZplan planning reports

## From EZplan 

```shell
python batchCompareStudies.py --base_path /media/developer/Storage1/HFRStudy-RUN2/images --output batch_report_RUN2 --output-path ./CurrentReports/RUN2_4/  --excel 
```

## From Slicer

```shell
python batch_stem_analysis.py \
   --image-root  /media/developer/Storage1/HFRStudy-RUN2/classif_SORT_04/ \
   --planning-root  /media/developer/Storage1/HFRStudy-RUN2/images/H001 \
   --stl-folder /media/developer/Storage1/HFRStudy-RUN2/Implants4EZplan \
   --slicer-extra-arg=--qt-disable-translate
```
