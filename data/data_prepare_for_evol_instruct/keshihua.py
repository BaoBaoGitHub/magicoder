import matplotlib.pyplot as plt

# 数据
occurrences = [0, 1, 2, 3, 4, 5, 6]
entry_counts = [173, 4138, 5661, 421, 8, 1, 1]

# 创建条形图
plt.figure(figsize=(8, 6))  # 设置图表尺寸
bars = plt.bar(occurrences, entry_counts, color='skyblue')  # 绘制条形图

# 添加标题和轴标签
plt.title("Distribution of '高质量' Occurrences in Dataset Entries", fontsize=14)
plt.xlabel("Number of Occurrences of '高质量'", fontsize=12)
plt.ylabel("Number of Entries", fontsize=12)

# 设置X轴刻度
plt.xticks(occurrences)

# 添加Y轴网格线
plt.grid(axis='y', linestyle='--', alpha=0.7)

# 在条形上方添加数据标签
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, height, str(int(height)), 
             ha='center', va='bottom', fontsize=10)

# 调整布局并显示图表
plt.tight_layout()
plt.show()