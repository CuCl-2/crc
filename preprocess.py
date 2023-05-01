import SimpleITK as sitk
from nipype.interfaces.ants import N4BiasFieldCorrection
import warnings
import os

def correct_bias(in_file, out_file, image_type=sitk.sitkFloat64):
    """
    Corrects the bias using ANTs N4BiasFieldCorrection. If this fails, will then attempt to correct bias using SimpleITK
    :param in_file: nii文件的输入路径
    :param out_file: 校正后的文件保存路径名
    :return: 校正后的nii文件全路径名
    """
    # 使用N4BiasFieldCorrection校正MRI图像的偏置场
    correct = N4BiasFieldCorrection()
    correct.inputs.input_image = in_file
    correct.inputs.output_image = out_file
    try:
        done = correct.run()
        return done.outputs.output_image
    except IOError:
        warnings.warn(RuntimeWarning("ANTs N4BIasFieldCorrection could not be found."
                                     "Will try using SimpleITK for bias field correction"
                                     " which will take much longer. To fix this problem, add N4BiasFieldCorrection"
                                     " to your PATH system variable. (example: EXPORT PATH=${PATH}:/path/to/ants/bin)"))
        print("ANTs N4BIasFieldCorrection could not be found."
                                     "Will try using SimpleITK for bias field correction"
                                     " which will take much longer. To fix this problem, add N4BiasFieldCorrection"
                                     " to your PATH system variable. (example: EXPORT PATH=${PATH}:/path/to/ants/bin)")
        input_image = sitk.ReadImage(in_file, image_type)
        output_image = sitk.N4BiasFieldCorrection(input_image, input_image > 0)
        sitk.WriteImage(output_image, out_file)
        return os.path.abspath(out_file)
    
def resampleVolume(outspacing, vol, type):
    """
    将体数据重采样的指定的spacing大小\n
    paras：
    outpacing：指定的spacing，例如[1,1,1]
    vol：sitk读取的image信息，这里是体数据
    type：指定插值方法，一般对image采取线性插值，对label采用最近邻插值
    return：重采样后的数据
    """
    outsize = [0, 0, 0]
    # 读取文件的size和spacing信息
    inputsize = vol.GetSize()
    inputspacing = vol.GetSpacing()
 
    transform = sitk.Transform()
    transform.SetIdentity()
    # 计算改变spacing后的size，用物理尺寸/体素的大小
    outsize[0] = round(inputsize[0] * inputspacing[0] / outspacing[0])
    outsize[1] = round(inputsize[1] * inputspacing[1] / outspacing[1])
    outsize[2] = round(inputsize[2] * inputspacing[2] / outspacing[2])
 
    # 设定重采样的一些参数
    resampler = sitk.ResampleImageFilter()
    resampler.SetTransform(transform)
    # 图像使用线性插值，标签使用最近邻插值
    if type == 'linear':
        resampler.SetInterpolator(sitk.sitkLinear)
        resampler.SetOutputPixelType(sitk.sitkFloat32)  # image用float32存
    else:
        resampler.SetInterpolator(sitk.sitkNearestNeighbor)
        resampler.SetOutputPixelType(sitk.sitkUInt8)  # 标签用int8存储
    resampler.SetOutputOrigin(vol.GetOrigin())
    resampler.SetOutputSpacing(outspacing)
    resampler.SetOutputDirection(vol.GetDirection())
    resampler.SetSize(outsize)
    newvol = resampler.Execute(vol)
    return newvol

root_path = './data_src'
data_dir = os.listdir(root_path)
data_dir.sort()
print(data_dir)

image_path = 'HRT2_image.nii.gz'
label_path = 'HRT2_segmentation.nii'
image_n4_path = 'HRT2_image_n4.nii.gz'

# for i in data_dir:
#     image = sitk.ReadImage(os.path.join(root_path, i, image_path))
#     label = sitk.ReadImage(os.path.join(root_path, i, label_path))
#     # print(image.GetSize(), image.GetSpacing(), label.GetSize(), label.GetSpacing())
#     # print(image.GetSize() == label.GetSize(), image.GetSpacing() == label.GetSpacing())
#     # N4
#     # correct_bias(os.path.join(root_path,i,image_path), os.path.join(root_path,i,image_n4_path))
#     image_n4 = sitk.ReadImage(os.path.join(root_path, i, image_n4_path))
#     label.CopyInformation(image_n4)
#     print(image_n4.GetSize(), image_n4.GetSpacing(), label.GetSize(), label.GetSpacing())
#     # Resample to 0.5 × 0.5 × 4
#     image_resample = resampleVolume([0.5, 0.5, 4], image_n4, 'linear')
#     label_resample = resampleVolume([0.5, 0.5, 4], label, 'else')
#     # print(image_resample.GetSize(), image_resample.GetSpacing(), label_resample.GetSize(), label_resample.GetSpacing())
#     sitk.WriteImage(image_resample, os.path.join(root_path, i, 'HRT2_image_n4_resample.nii.gz'))
#     sitk.WriteImage(label_resample, os.path.join(root_path, i, 'HRT2_segmentation_resample.nii'))
    

# check for data augmentation rotation
for i in data_dir:
    print(i)
    image = sitk.ReadImage(os.path.join(root_path, i, image_path))
    label = sitk.ReadImage(os.path.join(root_path, i, label_path))
    print(image.GetSize(), image.GetSpacing())