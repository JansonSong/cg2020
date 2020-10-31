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
