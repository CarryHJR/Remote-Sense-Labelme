## README
需求是，对于高分6的数据，随便一个tiff就是`10000*20000`左右的影像，用envi打开有明显的延迟卡顿，目前的算法是将影像划分为256*256的正方形，对每个正方形标注对应的类别，如

![image](https://upload-images.jianshu.io/upload_images/141140-49ef706329ac0642.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

## 源代码
[https://github.com/CarryHJR/Remote-Sense-Labelme](https://github.com/CarryHJR/Remote-Sense-Labelme)
## 样例数据
https://github.com/CarryHJR/Remote-Sense-Labelme/data

## 使用方式
样例命令
```
python main.py --path  data/GF6_WFV_E100.0_N40.2_20190126_L1A1119842986-3.jpeg
```
1. 通过方向键控制当前方框的移动
2. 按下数字键1 2 3 4后会改变框的颜色，分别对应4个类别
3. control+鼠标自适应放缩
4. 可以通过鼠标进行框选，然后配合数字键进行大区域标注
5. 鼠标双击改变当前方框的位置

## 注意事项
1. 需要将tiff文件收取rgb三通道转为jpeg格式
以高分6为例
```
gdal_translate test.tiff test-rgb.jpeg -ot Byte -of JPEG -scale  -b 3 -b 2 -b 1
```
2. 对于左上角第一个方格不要按左方向键和上方向键
## 设计思路
1. 实现自适应放缩的image viewer
2. 实现方框的移动和改变颜色
3. 实现框选和改变选中区域的颜色
4. 根据每个方块的颜色来保存
