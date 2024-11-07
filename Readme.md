# This is a muscle segmentation pipeline.

Before procedding, make sure you have the following tools, including FSL, Mrtirx3, itksnap, python3 and python packages listed in the requirement.txt

## 1. convert dicom to nii

After getting the raw data, which usually ends in .dcm, you need to convert it into .nii.gz to make convenience for afterwards operations.

```
mrconvert [input_dir_of_dcm_files] [output_path/converted.nii.gz]

```

An example is provided in [mrtrix3](https://mrtrix.readthedocs.io/en/dev/tips_and_tricks/dicom_handling.html)

## 2. splitting left and right legs

The original data consists of left and right thighs together, you need to split them into left_thigh and right_thigh from the middle, respectively.

```
python3 split_middle.py -f [target_path/converted.nii.gz]
```

The above command will generate two files at [target_path] with the name of converted_left.nii.gz and converted_right.nii.gz, respectively.

## 3. femur segmentation

If you only need to deal with baseline images and without dealing followup data, then you can skip this step. Otherwise, you need to run following operations to both baseline and followup images.

1. Open the itksnap 
2. Load the baseline image  (I take a baseline image as an example, don't forget followup ones later)
3. Use the 'snake' tool to bound the intrest area around the femur. You need to adjust the bounding box in three views respectively to make the bounding box to fit the femur as close as possible
4. Click 'Segment 3D' (indicates by the mouse cursor) on the left column
5. Modify the lower and upper threshold. Remember that the blue color indicates the background and white color indicates foreground. We want the femur (white) to be surrounded by blue color.
You need to check three views respectively to make femur covered by white color and the surrounding areas of femur covered by blue color such that the algorithm will not connect unexpected areas.
6. Click 'Next' (indicates by the mouse cursor)
7. Click 'Add bubble at cursor' and modify the bubble radius. The bubble at curosr should not exceed the femur.
8. Click 'Next' (indicates by the mouse cursor)
9. Now click 'run' and monitor the progress. You can modify the step size to change the growing speed. When monitoring the process, if you see the growing regions are not as expected, you shuold return to step 5.
You may also notice that some femur are not connected, we will fix that with manually annotation in the following step.
10. 
