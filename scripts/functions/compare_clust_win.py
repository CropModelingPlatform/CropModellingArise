# -*- coding: utf-8 -*-
"""
Created on Wed May 31 09:54:15 2023

@author: MIDINGOYI
"""

import pyodbc
import pandas as pd
from path import Path
import matplotlib.pyplot as plt



def compare_results(path_to_clust_db, path_to_win_db):

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
    
    
    merged_df[['lat', 'lon', 'year', 'Fert', "option"]] = merged_df['Idsim'].str.split("_", expand=True)
    merged_df["IdClim"] = merged_df["lat"]+"_"+ merged_df["lon"]
    
    merged_df["diff"] = merged_df["SoilN_x"]-merged_df["SoilN_y"]
    
    merged_df["diff"].sum()
    

    # Création du graphe
    plt.plot(merged_df["SoilN_x"], merged_df["SoilN_y"])
    plt.xlabel('SoilN_clust')
    plt.ylabel('SoilN_win')
    plt.title('Graphe SoilN_clust en fonction de SoilN_win')
    plt.legend()
    plt.show()
    



