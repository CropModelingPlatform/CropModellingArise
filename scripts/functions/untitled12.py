# -*- coding: utf-8 -*-
"""
Created on Wed May 31 16:10:10 2023

@author: MIDINGOYI
"""
import pandas as pd
import matplotlib.pyplot as plt

# Créer un DataFrame de test
df = pd.DataFrame({
    'model': ['stics', 'dssat', 'celsius', 'stics', 'dssat', 'celsius'],
    'x': [1, 2, 3, 4, 5, 6],
    'y': [2, 4, 6, 8, 10, 12]
})

# Grouper les données par modèle
grouped = df.groupby('model')

# Tracer les courbes pour chaque modèle dans des différents plots
fig, axs = plt.subplots(ncols=len(grouped))
colors = ['r', 'g', 'b', 'y', '', 'c']
for i, (name, group) in enumerate(grouped):
    axs[i].plot(group['x'], group['y'], label=name, color=colors[i])
    axs[i].legend()
    axs[i].set_xlabel('x')
    axs[i].set_ylabel('y')
    axs[i].set_title(name)
    plt.subplots_adjust(wspace=0.5)

# Enregistrer le plot dans un fichier PDF
plt.savefig('d:/Docs/test/plot.pdf')

# Afficher le plot
plt.show()






import pandas as pd
import matplotlib.pyplot as plt

# Créer un DataFrame de test
df = pd.DataFrame({
    'model': ['stics', 'dssat', 'celsius', 'stics', 'dssat', 'celsius'],
    'LAI_x': [1, 2, 3, 4, 5, 6],
    'LAI_y': [2, 4, 6, 8, 10, 12],
    'NEO_x': [1.5, 2.5, 3.5, 4.5, 5.5, 6.5],
    'NEO_y': [2.5, 4.5, 6.5, 8.5, 10.5, 12.5],
    'GPP_x': [2, 3, 4, 5, 6, 7],
    'GPP_y': [3, 5, 7, 9, 11, 13]
})

grouped = df.groupby('model')

models = list(df["model"].unique())
var = ["LAI", "NEO", "GPP"]
# Tracer les graphes pour chaque modèle et chaque variable
fig, axs = plt.subplots(nrows=len(var), ncols=len(models), figsize=(10, 15))
axs = axs.flatten()
k = 0
for var_index, var_name in enumerate(var):
    for i, (name, group) in enumerate(grouped):
        i = i + k
        axs[i].plot(group[var_name+'_x'], group[var_name+'_y'], label=var_name, color='r')
        axs[i].set_xlabel('cluster')
        axs[i].set_ylabel('windows')
        axs[i].set_title(name)
        axs[i].legend()
        plt.subplots_adjust(wspace=0.5, hspace=0.3)
    k = k +len(models)


# Enregistrer le plot dans un fichier PDF
plt.savefig('d:/Docs/test/plot.pdf')

# Afficher le plot
plt.show()








import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Créer un DataFrame de test
df = pd.DataFrame({
    'model': ['stics', 'dssat', 'celsius', 'stics', 'dssat', 'celsius'],
    'LAI_x': [1, 2, 3, 4, 5, 6],
    'LAI_y': [2, 4, 6, 8, 10, 12],
    'NEO_x': [1.5, 2.5, 3.5, 4.5, 5.5, 6.5],
    'NEO_y': [2.5, 4.5, 6.5, 8.5, 10.5, 12.5],
    'GPP_x': [2, 3, 4, 5, 6, 7],
    'GPP_y': [3, 5, 7, 9, 11, 13]
})

# Liste des variables à tracer
variables = ['LAI', 'NEO', 'GPP']

# Créer un fichier PDF
with PdfPages('d:/Docs/test/plot.pdf') as pdf:
    # Tracer les graphes pour chaque variable
    for var in variables:
        x = var + '_x'
        y = var + '_y'
        fig, axs = plt.subplots(nrows=3, ncols=1, figsize=(10, 15))
        axs = axs.flatten()
        for i, model in enumerate(['stics', 'dssat', 'celsius']):
            group = df[df['model'] == model]
            axs[i].scatter(group[x], group[y], label=model, color='r')
            axs[i].set_xlabel('Observed')
            axs[i].set_ylabel('Estimated')
            axs[i].set_title(model)
            axs[i].legend()
        pdf.savefig()
        plt.close()
        

import pandas as pd
import matplotlib.pyplot as plt

# Créer un DataFrame de test
df = pd.DataFrame({
    'model': ['stics', 'dssat', 'celsius', 'stics', 'dssat', 'celsius'],
    'LAI_x': [1, 2, 3, 4, 5, 6],
    'LAI_y': [2, 4, 6, 8, 10, 12],
    'NEO_x': [1.5, 2.5, 3.5, 4.5, 5.5, 6.5],
    'NEO_y': [2.5, 4.5, 6.5, 8.5, 10.5, 12.5],
    'GPP_x': [2, 3, 4, 5, 6, 7],
    'GPP_y': [3, 5, 7, 9, 11, 13]
})

# Liste des variables à tracer
variables = ['LAI', 'NEO', 'GPP']
fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(15, 5))
# Tracer les graphes pour chaque variable
for pp, var in enumerate(variables):
    x = var + '_x'
    y = var + '_y'
    for i, model in enumerate(['stics', 'dssat', 'celsius']):
        group = df[df['model'] == model]
        axs[i].plot(group[x], group[y], label=model, color='r')
        axs[i].set_xlabel('Observed')
        axs[i].set_ylabel('Estimated')
        axs[i].set_title(model)
        axs[i].legend()
    plt.show()