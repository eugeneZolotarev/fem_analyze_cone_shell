import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np


df = pd.read_csv("../mesh_test/mesh_test.csv")

# Превращаем таблицу в матрицу для графиков
pivot_df = df.pivot(index='Elements_Along', columns='Elements_Between', values='Eigenvalue')
Z = pivot_df.values
X_unique = pivot_df.columns.values
Y_unique = pivot_df.index.values
X, Y = np.meshgrid(X_unique, Y_unique)

# 2. Расчет градиента (скорости изменения)
# np.gradient вычисляет производные по обеим осям
dy, dx = np.gradient(Z, Y_unique, X_unique)
grad_norm = np.sqrt(dx**2 + dy**2)

# 3. Визуализация
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Левый график: Сами значения (Z)
im1 = ax1.imshow(Z, extent=[X.min(), X.max(), Y.min(), Y.max()],
                 origin='lower', cmap='viridis', aspect='auto', interpolation='bilinear')
ax1.set_title('Значения Eigenvalue')
ax1.set_xlabel('Elements_Between')
ax1.set_ylabel('Elements_Along')
plt.colorbar(im1, ax=ax1)

# Правый график: Модуль градиента (насколько быстро меняется Z)
im2 = ax2.imshow(grad_norm, extent=[X.min(), X.max(), Y.min(), Y.max()],
                 origin='lower', cmap='magma', aspect='auto', interpolation='bilinear')
ax2.set_title('Скорость изменения (Градиент)')
ax2.set_xlabel('Elements_Between')
plt.colorbar(im2, ax=ax2)

# Поиск зоны плато: где градиент меньше 10% от максимального
threshold = 0.1 * np.nanmax(grad_norm)
ax1.contour(X, Y, grad_norm, levels=[threshold], colors='red', linewidths=2)

fig1 = plt.figure(figsize=(18, 5))

# --- ГРАФИК 2: Зависимость от Elements_Between ---
ax2 = fig1.add_subplot(121)
for along_val in df['Elements_Along'].unique():
    subset = df[df['Elements_Along'] == along_val]
    ax2.plot(subset['Elements_Between'], subset['Eigenvalue'], marker='o', label=f'Along={along_val}')
ax2.set_title('Eigenvalue vs Elements_Between')
ax2.set_xlabel('Elements_Between')
ax2.set_ylabel('Eigenvalue')
ax2.grid(True, linestyle='--')
# ax2.legend() # Можно включить, если значений Along немного

# --- ГРАФИК 3: Зависимость от Elements_Along ---
ax3 = fig1.add_subplot(122)
for between_val in df['Elements_Between'].unique():
    subset = df[df['Elements_Between'] == between_val]
    ax3.plot(subset['Elements_Along'], subset['Eigenvalue'], marker='s', label=f'Between={between_val}')
ax3.set_title('Eigenvalue vs Elements_Along')
ax3.set_xlabel('Elements_Along')
ax3.set_ylabel('Eigenvalue')
ax3.grid(True, linestyle='--')
ax3.legend()

plt.tight_layout()
plt.show()