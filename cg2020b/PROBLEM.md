（1）

```python
canvas[height - 1 - y, x] = color
```

原文件中，初始时，是这样画图的，但是我感觉正确的就应该是

```
canvas[y, x] = color
```

（2）
测试样例中有这样一条语句
```
drawEllipse ellipse1 100 100 500 400
rotate ellipse1 100 100 45
```
但是不进行对椭圆的旋转，所以这句测试样例可以忽略吗？

（3）椭圆画出来之后，感觉有点离散，是否是算法出现了问题？

（5）曲线的基点没有显示出来，效果可能不是很好。

（7）直线实现的算法，在线段的开始地方，会有一点的偏差

（8）旋转的细节还要注意一下


### 拓展功能
（1）实现可以通过鼠标在画布中选择

（2）可以保存画布

（3）可以删除选中的元素

（4）绘制曲线的时候，会显示控制点，并且选择某个曲线的时候也会显示控制点，
但是如果不选择的话，不显示控制点