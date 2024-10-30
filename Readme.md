# This is a muscle segmentation pipeline.

## 1. convert dicom to nii

After getting the raw data, which usually ends in .dcm, you need to convert it into .nii.gz to make convenience for the afterwards operations.

```
mrconvert [input_dir] [output_file_name]
```