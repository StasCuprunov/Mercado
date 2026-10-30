import pandas as pd
from pathlib import Path
import importlib
import numpy as np

import data_preparation

def convert_data_to_cleaned_version():
    """
        Daten in gesäuberte Form als parquet-Dateien speichern

        Säuberung am Beispiel von products mit den Kategorienamen
        - Vor der Säuberung waren deutlich mehr Kategorien aufgrund falscher Schreibweise vorhanden. Ohne die Bereinigung wären sie als eigene Kategorie
          angesehen worden. Durch die Säuberung werden nun korrekterweise die Produkte kategorisiert, so dass bei Analysen in Bezug auf Kategorien
          die passenden Produkte genommen werden.
    """
    # Pfade bestimmen
    destination_path = "cleaned_data"
    folder = Path(destination_path)
    folder.mkdir(parents=True, exist_ok=True)
    path_prefix = Path.cwd() / "data/"
    path_cleaned_data_prefix = Path.cwd() / destination_path

    # Säuberung der Daten
    convert_payments_to_cleaned_version(path_prefix, path_cleaned_data_prefix)
    convert_pilot_support_to_cleaned_version(path_prefix, path_cleaned_data_prefix)
    convert_service_experiment_to_cleaned_version(path_prefix, path_cleaned_data_prefix)
    convert_service_observation_to_cleaned_version(path_prefix, path_cleaned_data_prefix)
    convert_categories_to_cleaned_version(path_prefix, path_cleaned_data_prefix)
    convert_reviews_to_cleaned_version(path_prefix, path_cleaned_data_prefix)
    convert_orders_to_cleaned_version(path_prefix, path_cleaned_data_prefix)
    convert_items_to_cleaned_version(path_prefix, path_cleaned_data_prefix)
    convert_geolocation_to_cleaned_version(path_prefix, path_cleaned_data_prefix)
    convert_products_to_cleaned_version(path_prefix, path_cleaned_data_prefix)
    convert_sellers_to_cleaned_version(path_prefix, path_cleaned_data_prefix)
    convert_customers_to_cleaned_version(path_prefix, path_cleaned_data_prefix)

def convert_payments_to_cleaned_version(path_prefix, path_cleaned_data_prefix):
    """ payments.parquet erstellen
    """
    file_name = "payments"
    df = pd.read_csv(path_prefix  / f"{file_name}.csv")
    df.to_parquet(path_cleaned_data_prefix / f"{file_name}.parquet", engine="pyarrow", index=False)

def convert_pilot_support_to_cleaned_version(path_prefix, path_cleaned_data_prefix):
    """ pilot_support.parquet erstellen
    """
    file_name = "pilot_support"
    df = pd.read_csv(path_prefix  / f"{file_name}.csv")
    df.to_parquet(path_cleaned_data_prefix / f"{file_name}.parquet", engine="pyarrow", index=False)

def convert_service_experiment_to_cleaned_version(path_prefix, path_cleaned_data_prefix):
    """ service_experiment.parquet erstellen
    """
    file_name = "service_experiment"
    df = pd.read_csv(path_prefix  / f"{file_name}.csv")
    df.to_parquet(path_cleaned_data_prefix / f"{file_name}.parquet", engine="pyarrow", index=False)

def convert_service_observation_to_cleaned_version(path_prefix, path_cleaned_data_prefix):
    """ service_observation.parquet erstellen
    """
    file_name = "service_observation"
    df = pd.read_csv(path_prefix  / f"{file_name}.csv")
    df.to_parquet(path_cleaned_data_prefix / f"{file_name}.parquet", engine="pyarrow", index=False)

def convert_categories_to_cleaned_version(path_prefix, path_cleaned_data_prefix):
    """ categories.parquet erstellen
    """
    file_name = "categories"
    df = pd.read_csv(path_prefix  / f"{file_name}.csv")
    df.to_parquet(path_cleaned_data_prefix / f"{file_name}.parquet", engine="pyarrow", index=False)


def convert_reviews_to_cleaned_version(path_prefix, path_cleaned_data_prefix):
    """ reviews.parquet erstellen
    """
    file_name = "reviews"
    df = pd.read_csv(path_prefix  / f"{file_name}.csv")
    df.to_parquet(path_cleaned_data_prefix / f"{file_name}.parquet", engine="pyarrow", index=False)

def convert_orders_to_cleaned_version(path_prefix, path_cleaned_data_prefix):
    """ orders.parquet erstellen
    """
    file_name = "orders"
    order_delivered_customer_date_variable = "order_delivered_customer_date"
    order_estimated_delivery_date_variable = "order_estimated_delivery_date"
    order_purchase_timestamp_variable = "order_purchase_timestamp"
    review_answer_timestamp_variable = "review_answer_timestamp"
    order_id_variable = "order_id"
    
    df = pd.read_csv(path_prefix  / f"{file_name}.csv")

    # Attribut Verspätung hinzufügen
    df["delay"] = df[order_delivered_customer_date_variable] > df[order_estimated_delivery_date_variable]

    df[order_delivered_customer_date_variable] = pd.to_datetime(df[order_delivered_customer_date_variable])
    df[order_purchase_timestamp_variable] = pd.to_datetime(df[order_purchase_timestamp_variable])

    # Attribut Lieferdauer hinzufügen
    df["delivery_time_in_days"] = np.select(
    [
        (df[order_delivered_customer_date_variable] - df[order_purchase_timestamp_variable]).dt.days <= 7,
        (df[order_delivered_customer_date_variable] - df[order_purchase_timestamp_variable]).dt.days.between(8, 14),
        (df[order_delivered_customer_date_variable] - df[order_purchase_timestamp_variable]).dt.days.between(15, 21),
        (df[order_delivered_customer_date_variable] - df[order_purchase_timestamp_variable]).dt.days > 21
    ],
    ["<= 7", "8 to 14", "15 to 21", "> 21"],
    default="no value"
    )

    # Attribut schlechte Bewertung hinzufügen
    df_reviews = pd.read_parquet(path_cleaned_data_prefix / "reviews.parquet")

    # Pro order_id den aktuellsten review_score mappen
    last_review_values = (
        df_reviews.dropna(subset=[review_answer_timestamp_variable])
            .sort_values([review_answer_timestamp_variable, "review_id"], na_position="first")
            .drop_duplicates(order_id_variable, keep="last")
            .set_index(order_id_variable)["review_score"]
    )
    df["bad_review"] = df[order_id_variable].map(last_review_values) <= 2
    
    df.to_parquet(path_cleaned_data_prefix / f"{file_name}.parquet", engine="pyarrow", index=False)

def convert_items_to_cleaned_version(path_prefix, path_cleaned_data_prefix):
    """ items.parquet erstellen
        Es wurden Duplikate entfernt, da eine Dopplung keinen Mehrwert hat.
    """
    file_name = "items"
    df = pd.read_csv(path_prefix  / f"{file_name}.csv")
    df = df.drop_duplicates()
    df.to_parquet(path_cleaned_data_prefix / f"{file_name}.parquet", engine="pyarrow", index=False)

def convert_geolocation_to_cleaned_version(path_prefix, path_cleaned_data_prefix):
    """ geolocation.parquet erstellen
        Es wurden Duplikate entfernt, da eine Dopplung keinen Mehrwert hat.
        
        Die Postleitzahl waren nicht mit führenden Nullen. Das Attribut wurde abgeändert zu einen String mit führenden Nullen als fünfstellige Wert.
    """
    file_name = "geolocation"
    zip_code_variable = "geolocation_zip_code_prefix"
    
    df = pd.read_csv(path_prefix  / f"{file_name}.csv")
    df = df.drop_duplicates()
    df[zip_code_variable] = df[zip_code_variable].astype("string").str.zfill(5)
    df.to_parquet(path_cleaned_data_prefix / f"{file_name}.parquet", engine="pyarrow", index=False)

def convert_products_to_cleaned_version(path_prefix, path_cleaned_data_prefix):
    """ products.parquet erstellen
        Die Kategorien von den Produkten wurden oftmals falsch geschrieben. Anhand der Wortähnlichkeit wurden die Kategorien der Produkte mit den
        Kategoriennamen der categorie.parquet verglichen und abgeändert.
        
        Die Anzahl an Fotos wurde als Ganzzahl mit Minimum 0 abgebildet, da es eine Ganzzahl ist und weniger als 0 Fotos nicht möglich sind. NaN kann 
        als 0 gedeutet werden.
    """
    file_name = "products"
    category_variable = "product_category_name"
    quantity_variable = "product_photos_qty"
    
    df = pd.read_csv(path_prefix  / f"{file_name}.csv")
    df[category_variable] = df[category_variable].str.lower()
    df[category_variable] = df[category_variable].replace({
        "acma_mesa_banho": "cama_mesa_banho",
        "acsa_construcao": "casa_construcao",
        "agro_industria_e_comercio ": "agro_industria_e_comercio",
        "alimentos_bebdias": "alimentos_bebidas",
        "appelaria": "papelaria",
        "artes ": "artes",
        "atuomotivo": "automotivo",
        "automoitvo": "automotivo",
        "automotivo ": "automotivo",
        "automotvio": "automotivo",
        "autmootivo" : "automotivo",
        "audoi": "audio",
        "bebes ": "bebes",
        "bebse": "bebes",
        "beebs": "bebes",
        "beleaz_saude": "beleza_saude",
        "beleza_asude": "beleza_saude",
        "beleza_saude ": "beleza_saude",
        "beleza_saued": "beleza_saude",
        "beleza_suade": "beleza_saude",
        "brinqeudos": "brinquedos",
        "brinquedos ": "brinquedos",
        "briqnuedos": "brinquedos",
        "brniquedos": "brinquedos",
        "caam_mesa_banho": "cama_mesa_banho",
        "cama_emsa_banho": "cama_mesa_banho",
        "cama_meas_banho": "cama_mesa_banho",
        "cama_mesa_bahno": "cama_mesa_banho",
        "cama_mesa_banho ":"cama_mesa_banho",
        "cama_mesa_banoh": "cama_mesa_banho",
        "cama_mesa_bnaho": "cama_mesa_banho",
        "casa_conforto ": "casa_conforto",
        "climatizacao ": "climatizacao",
        "cmaa_mesa_banho": "cama_mesa_banho",
        "cnosoles_games": "consoles_games",
        "consoles_games ": "consoles_games",
        "construcao_ferramentas_construcao ": "construcao_ferramentas_construcao",
        "construcao_ferramentas_cosntrucao": "construcao_ferramentas_construcao",
        "construcao_ferramentas_jardim ": "construcao_ferramentas_jardim",
        "cool_stuff ": "cool_stuff",
        "cool_sutff": "cool_stuff",
        "cool_tsuff": "cool_stuff",
        "cosntrucao_ferramentas_iluminacao": "construcao_ferramentas_iluminacao",
        "ebleza_saude": "beleza_saude",
        "eeltrodomesticos": "eletrodomesticos",
        "eletrodomesticos": "eletrodomesticos",
        "eletrodomesticos ": "eletrodomesticos",
        "eletrodomesticos_2 ": "eletrodomesticos_2",
        "eletronicos ": "eletronicos",
        "eletroniocs": "eletronicos",
        "eletroodmesticos": "eletrodomesticos",
        "eletroportateis ": "eletroportateis",
        "epsorte_lazer": "esporte_lazer",
        "esporet_lazer": "esporte_lazer",
        "esporte_alzer": "esporte_lazer",
        "esporte_laezr": "esporte_lazer",
        "esporte_lazer ": "esporte_lazer",
        "esporte_lazre": "esporte_lazer",
        "esprote_lazer": "esporte_lazer",
        "etlefonia": "telefonia",
        "fahsion_calcados": "fashion_calcados",
        "fashion_bolsas_e_acesosrios": "fashion_bolsas_e_acessorios",
        "fashion_bolsas_e_acessoiros": "fashion_bolsas_e_acessorios",
        "fashion_bolsas_e_acessorios ": "fashion_bolsas_e_acessorios",
        "fashion_roupa_masculina ": "fashion_roupa_masculina",
        "ferramentas_jardim ": "ferramentas_jardim",
        "ferramentas_jardmi": "ferramentas_jardim",
        "ferramentsa_jardim": "ferramentas_jardim",
        "ferrametnas_jardim": "ferramentas_jardim",
        "fsahion_bolsas_e_acessorios": "fashion_bolsas_e_acessorios",
        "ifnormatica_acessorios": "informatica_acessorios",
        "informatcia_acessorios": "informatica_acessorios",
        "informatiac_acessorios": "informatica_acessorios",
        "informatica_acessorios ": "informatica_acessorios",
        "informatica_acsesorios":  "informatica_acessorios",
        "informtaica_acessorios": "informatica_acessorios",
        "inofrmatica_acessorios": "informatica_acessorios",
        "instrumentos_musicais ": "instrumentos_musicais",
        "instrumetnos_musicais": "instrumentos_musicais",
        "leetronicos": "eletronicos",
        "livors_interesse_geral": "livros_interesse_geral",
        "livros_tecnicos ": "livros_tecnicos",
        "malas_acessorios ": "malas_acessorios",
        "malas_acsesorios": "malas_acessorios",
        "marekt_place": "market_place",
        "moveis_cozinha_area_de_servico_jantar_e_jardim ": "moveis_cozinha_area_de_servico_jantar_e_jardim",
        "moveis_decoarcao": "moveis_decoracao",
        "moveis_decoracao ": "moveis_decoracao",
        "moveis_decorcaao": "moveis_decoracao",
        "moveis_edcoracao": "moveis_decoracao",
        "moveis_escritorio ": "moveis_escritorio",
        "moveis_esrcitorio": "moveis_escritorio",
        "moveis_sala ": "moveis_sala",
        "movesi_decoracao": "moveis_decoracao",
        "movies_decoracao": "moveis_decoracao",
        "ocol_stuff": "cool_stuff",
        "omveis_decoracao": "moveis_decoracao",
        "omveis_sala": "moveis_sala",
        "papealria": "papelaria",
        "papelaira": "papelaria",
        "papelaria ": "papelaria",
        "perfumarai": "perfumaria",
        "perfumaria ": "perfumaria",
        "perfumraia": "perfumaria",
        "perufmaria": "perfumaria",
        "pet_shop ": "pet_shop",
        "pet_shpo": "pet_shop",
        "rbinquedos": "brinquedos",
        "relogios_presentes ": "relogios_presentes",
        "relogios_presetnes": "relogios_presentes",
        "relogios_presnetes": "relogios_presentes",
        "relogios_rpesentes": "relogios_presentes",
        "rleogios_presentes": "relogios_presentes",
        "seporte_lazer": "esporte_lazer",
        "telefnoia": "telefonia",
        "telefoina": "telefonia",
        "telefonia ": "telefonia",
        "tleefonia": "telefonia",
        "telfeonia_fixa": "telefonia_fixa",
        "uatomotivo": "automotivo",
        "utilidades_doemsticas": "utilidades_domesticas",
        "utilidades_domestcias": "utilidades_domesticas",
        "utilidades_domesticas ": "utilidades_domesticas",
        "utilidades_domesticsa": "utilidades_domesticas",
        "utilidades_dometsicas": "utilidades_domesticas",
        "utilidades_odmesticas": "utilidades_domesticas",
        "utilidadse_domesticas": "utilidades_domesticas",
        "utilidades_domestiacs": "utilidades_domesticas"
    })
    df[quantity_variable] = df[quantity_variable].fillna(0).astype("Int64") 
    df.to_parquet(path_cleaned_data_prefix / f"{file_name}.parquet", engine="pyarrow", index=False)

def convert_sellers_to_cleaned_version(path_prefix, path_cleaned_data_prefix):
    """ sellers.parquet erstellen
        Die Postleitzahl waren nicht mit führenden Nullen. Das Attribut wurde abgeändert zu einen String mit führenden Nullen als fünfstellige Wert.

        Manche Städtenamen wurden falsch geschrieben oder hatten in ihren Namen den den zugehörigen Bundesstaat. Dies wurde korrigiert.
    """
    file_name = "sellers"
    zip_code_variable = "seller_zip_code_prefix"
    city_variable = "seller_city"
    costs_variable = "costs"
    seller_id_variable = "seller_id"
    
    df = pd.read_csv(path_prefix  / f"{file_name}.csv")
    df[zip_code_variable] = df[zip_code_variable].astype("string").str.zfill(5)
    df[city_variable] = df[city_variable].replace({
        "aguas claras df": "aguas claras",
        "andira-pr": "andira",
        "angra dos reis rj": "angra dos reis",
        "ao bernardo do campo": "sao bernardo do campo",
        "auriflama/sp": "auriflama",
        "balenario camboriu": "balneario camboriu",
        "barbacena/ minas gerais": "barbacena",
        "belo horizont": "belo horizonte",
        "brasilia df": "brasilia",
        "carapicuiba / sao paulo": "carapicuiba",
        "cariacica / es": "cariacica",
        "cascavael": "cascavel",
        "ferraz de  vasconcelos": "ferraz de vasconcelos",
        "floranopolis": "florianopolis",
        "garulhos": "guarulhos",
        "jacarei / sao paulo": "jacarei",
        "lages - sc": "lages",
        "maua/sao paulo": "maua",
        "mogi das cruses": "mogi das cruzes",
        "mogi das cruzes / sp": "mogi das cruzes",
        "novo hamburgo, rio grande do sul, brasil": "novo hamburgo",
        "pinhais/pr": "pinhais",
        "portoferreira": "porto ferreira",
        "ribeirao preto / sao paulo": "ribeirao preto",
        "ribeirao pretp": "ribeirao preto",
        "riberao preto": "ribeirao preto",
        "rio de janeiro / rio de janeiro": "rio de janeiro",
        "rio de janeiro \\rio de janeiro": "rio de janeiro",
        "rio de janeiro, rio de janeiro, brasil": "rio de janeiro",
        "s jose do rio preto": "sao jose do rio preto",
        "sando andre": "santo andre",
        "santa barbara d oeste": "santa barbara d'oeste",
        "santa barbara d´oeste": "santa barbara d'oeste",
        "santo andre/sao paulo": "santo andre",
        "sao  jose dos pinhais": "sao jose dos pinhais",
        "sao  paulo": "sao paulo",
        "sao bernardo do capo": "sao bernardo do campo",
        "sao jose do rio pret": "sao jose do rio preto",
        "sao jose dos pinhas": "sao jose dos pinhais",
        "sao miguel d'oeste": "sao miguel do oeste",
        "sao paluo": "sao paulo",
        "sao paulo - sp": "sao paulo",
        "sao paulo / sao paulo": "sao paulo",
        "sao paulo sp": "sao paulo",
        "sao paulop": "sao paulo",
        "sao pauo": "sao paulo",
        "sao sebastiao da grama/sp": "sao sebastiao da grama",
        "são paulo": "sao paulo",
        "sbc": "sao bernardo do campo",
        "sbc/sp": "sao bernardo do campo",
        "scao jose do rio pardo": "sao jose do rio pardo",
        "sp": "sao paulo",
        "sp / sp": "sao paulo",
        "tabao da serra": "taboao da serra"
    })

    # Attribut Gesamtumsatz erstellen
    df_items = pd.read_parquet(path_cleaned_data_prefix / "items.parquet")
    df_items[costs_variable] = df_items["price"] + df_items["freight_value"] # Zusammenrechnen der Kosten

    # Pro Händler aufsummieren
    costs_per_seller_id = df_items.groupby(seller_id_variable, as_index=False)[costs_variable].sum()

    # Verbinden der Summe mit dem jeweiligen HÄndler
    df = df.merge(costs_per_seller_id, on=seller_id_variable, how="left")
    df = df.rename(columns={costs_variable: "sales_volume"})

    df.to_parquet(path_cleaned_data_prefix / f"{file_name}.parquet", engine="pyarrow", index=False)

def convert_customers_to_cleaned_version(path_prefix, path_cleaned_data_prefix):
    """ customers.parquet erstellen
        Die Postleitzahl waren nicht mit führenden Nullen. Das Attribut wurde abgeändert zu einen String mit führenden Nullen als fünfstellige Wert.

        Manche Städtenamen wurden falsch geschrieben. Dies wurde anhand der Wortähnlichkeit und den dazugehörigen Bundesstaat angepasst.
    """
    file_name = "customers"
    zip_code_variable = "customer_zip_code_prefix"
    city_variable = "customer_city"
    
    df = pd.read_csv(path_prefix / f"{file_name}.csv")
    df[zip_code_variable] = df[zip_code_variable].astype("string").str.zfill(5)

    df[city_variable] = df[city_variable].replace({
        "arraial d ajuda": "arraial d'ajuda",
        "dias d avila": "dias d'avila",
        "embu": "embu das artes",
        "espigao do oeste": "espigao d'oeste",
        "estrela d oeste": "estrela d'oeste",
        "goitacazes": "campos dos goytacazes",
        "hidreletrica tucurui": "tucurui",
        "mogi-mirim": "mogi mirim",
        "palmeira d oeste": "palmeira d'oeste",
        "parati": "paraty",
        "piumhii": "piumhi",
        "santa barbara d oeste": "santa barbara d'oeste",
        "sao jorge do oeste": "sao jorge d'oeste",
    })
    df.to_parquet(path_cleaned_data_prefix / f"{file_name}.parquet", engine="pyarrow", index=False)