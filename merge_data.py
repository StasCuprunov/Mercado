import pandas as pd
import importlib
from pathlib import Path


def create_merged_tables():
    # Pfade bestimmen
    destination_path = "merged_data"
    folder = Path(destination_path)
    folder.mkdir(parents=True, exist_ok=True)
    path_source_prefix = Path.cwd() / "cleaned_data"
    path_destination_prefix = Path.cwd() / destination_path

    # Erstellen der verschmolzenen Tabellen
    create_merged_table_orders(path_source_prefix, path_destination_prefix)
    create_merged_table_products(path_source_prefix, path_destination_prefix)
    create_merged_table_orders_and_service_observation(path_source_prefix, path_destination_prefix)
    create_merged_table_orders_and_pilot_support(path_source_prefix, path_destination_prefix)
    create_merged_table_orders_and_service_experiment(path_source_prefix, path_destination_prefix)

def create_merged_table_orders(path_source_prefix, path_destination_prefix):
    """
        Bestelltabelle erstellen

        orders hat 99441 Einträge, diese Bestelltabelle hat nur 96478 Einträge, da nur ausgelieferte Bestellungen hier verwendet werden.
    """
    review_answer_timestamp_variable = "review_answer_timestamp"
    order_id_variable = "order_id"
    
    # parquet-Dateien holen
    df_orders = pd.read_parquet(path_source_prefix / "orders.parquet")
    df_customers = pd.read_parquet(path_source_prefix / "customers.parquet")
    df_reviews = pd.read_parquet(path_source_prefix / "reviews.parquet")
    
    # Nur Bestellungen, die geliefert worden sind, werden ausgewählt
    df_merged = df_orders.loc[df_orders["order_status"] == "delivered"].copy()
    
    # Verschmelzen orders und customers
    df_merged = df_merged.merge(df_customers, on="customer_id", how="inner")
    
    # letzten Review-Score hinzufügen
    last_review_values = (
        df_reviews.dropna(subset=[review_answer_timestamp_variable])
            .sort_values([review_answer_timestamp_variable, "review_id"], na_position="first")
            .drop_duplicates(order_id_variable, keep="last")
            .set_index(order_id_variable)["review_score"]
    )
    df_merged["last_review_score"] = df_merged[order_id_variable].map(last_review_values)

    df_merged.to_parquet(path_destination_prefix / "merged_orders_table.parquet", engine="pyarrow", index=False)

def create_merged_table_products(path_source_prefix, path_destination_prefix):
    """ Tabellen für Produkte erstellen

        items hat 112650 Einträge. Da nur gelieferte Bestellungen zählen, sinkt der Wert auf 110197
    """
    order_id_variable = "order_id"
    
    # parquet-Dateien holen
    df_items = pd.read_parquet(path_source_prefix / "items.parquet")
    df_sellers = pd.read_parquet(path_source_prefix / "sellers.parquet")
    df_products = pd.read_parquet(path_source_prefix / "products.parquet")
    df_categories = pd.read_parquet(path_source_prefix / "categories.parquet")
    df_orders = pd.read_parquet(path_source_prefix / "orders.parquet")

    # Entferne Zeilen, dessen order_status != delivered ist
    order_ids = df_orders.loc[df_orders["order_status"] != "delivered", order_id_variable]
    df_items = df_items.loc[~df_items[order_id_variable].isin(order_ids)].copy()

    # Zusammenführen
    df_merged = df_items.merge(df_sellers, on = "seller_id", how = "left")
    df_merged = df_merged.merge(df_products, on = "product_id", how = "left")
    df_merged = df_merged.merge(df_categories, on = "product_category_name", how = "left")

    df_merged.to_parquet(path_destination_prefix / "merged_products_table.parquet", engine="pyarrow", index=False)

def create_merged_table_orders_and_service_observation(path_source_prefix, path_destination_prefix):
    """ Bestelltabelle mit service observation verknüpfen
    
        service observation hat 95824 Einträge. Die Einträge sind gleich geblieben.
    """
    # parquet-Dateien holen
    df_orders_table = pd.read_parquet(path_destination_prefix / "merged_orders_table.parquet")
    df_service_observation = pd.read_parquet(path_source_prefix / "service_observation.parquet")

    df_merged = df_orders_table.merge(df_service_observation, on = "order_id", how = "inner")

    df_merged.to_parquet(path_destination_prefix / "merged_orders_and_service_observation_table.parquet", engine="pyarrow", index=False)

def create_merged_table_orders_and_pilot_support(path_source_prefix, path_destination_prefix):
    """ Bestelltabelle mit pilot support verknüpfen

        pilot support hat 40 Einträge. Nach der Verschmelzung hat es immer noch 40 Einträge.
    """
    # parquet-Dateien holen
    df_orders_table = pd.read_parquet(path_destination_prefix / "merged_orders_table.parquet")
    df_pilot_support = pd.read_parquet(path_source_prefix / "pilot_support.parquet")

    df_merged = df_orders_table.merge(df_pilot_support, on = "order_id", how = "inner")

    # Doppelte Spalte löschen
    df_merged = df_merged.drop(columns=["customer_unique_id_y"])
    df_merged = df_merged.rename(columns={"customer_unique_id_x": "customer_unique_id"})

    df_merged.to_parquet(path_destination_prefix / "merged_orders_and_pilot_support_table.parquet", engine="pyarrow", index=False)

def create_merged_table_orders_and_service_experiment(path_source_prefix, path_destination_prefix):
    """ Bestelltabelle mit service experiment verknüpfen

        Service experiment hat 92747 Einträge. Mit der Verschmelzung ist die Anzahl an Einträgen gleich geblieben.
    """
    # parquet-Dateien holen
    df_orders_table = pd.read_parquet(path_destination_prefix / "merged_orders_table.parquet")
    df_service_experiment = pd.read_parquet(path_source_prefix / "service_experiment.parquet")

    df_merged = df_orders_table.merge(df_service_experiment, on = "order_id", how = "inner")

    # Doppelte Spalte löschen
    df_merged = df_merged.drop(columns=["customer_unique_id_y"])
    df_merged = df_merged.rename(columns={"customer_unique_id_x": "customer_unique_id"})

    df_merged.to_parquet(path_destination_prefix / "merged_orders_and_service_experiment_table.parquet", engine="pyarrow", index=False)
    