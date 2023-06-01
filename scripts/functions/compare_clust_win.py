# -*- coding: utf-8 -*-
"""
Created on Wed May 31 09:54:15 2023

@author: MIDINGOYI
"""

import pyodbc
import pandas as pd
from path import Path
import matplotlib.pyplot as plt
import os



def compare_results(path_to_clust_db, path_to_win_db, plot_rep):
    

    constr1 = "DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={0};".format(Path(path_to_clust_db))
    conn1= pyodbc.connect(constr1, autocommit=False)
    
    
    constr2 = "DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={0};".format(Path(path_to_win_db))
    conn2= pyodbc.connect(constr2, autocommit=False)
    
    
    # Écrire la requête SQL pour sélectionner le champ de la table
    
    query = "SELECT Model, Idsim, Yield, Biom_ma, MaxLAI, SoilN, Nleac, Cron_ma, Transp, CumE FROM  SummaryOutput;"
    
    # Exécuter la requête et récupérer les résultats dans un DataFrame
    df1 = pd.read_sql(query, conn1)
    df2 = pd.read_sql(query, conn2)
    
    # Fermer la connexion
    conn1.close()
    conn2.close()
    
    # Afficher les premières lignes du DataFrame
    print(df1.head())
    print(df2.head())
    
    merged_df = pd.merge(df1, df2, on=['Model','Idsim'])
    
    grouped = merged_df.groupby('Model')
    
    models = list(merged_df["Model"].unique())
    var = ["Yield", "Biom_ma", "MaxLAI", "SoilN", "Nleac", "Cron_ma", "Transp", "CumE"]
    # Tracer les graphes pour chaque modèle et chaque variable
    fig, axs = plt.subplots(nrows=len(var), ncols=len(models), figsize=(10, 15)) #•10 15
    axs = axs.flatten()
    k = 0
    for var_index, var_name in enumerate(var):
        colors = ['r', 'g', 'b', 'y', 'c']
        for i, (name, group) in enumerate(grouped):
            color = colors[i]
            i = i + k
            axs[i].plot(group[var_name+'_x'], group[var_name+'_y'], label=var_name, color=color)
            axs[i].set_xlabel('cluster')
            axs[i].set_ylabel('windows')
            axs[i].set_title(name)
            axs[i].legend()
            plt.subplots_adjust(wspace=0.5, hspace=0.3)
        k = k +len(models)
    
    fig.tight_layout()

    # Enregistrer le plot dans un fichier PDF
    plt.savefig(os.path.join(plot_rep, 'plot.pdf'))
    
    # Afficher le plot
    plt.show()



