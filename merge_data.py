import pandas as pd
import importlib
from pathlib import Path


def create_merged_tables():
    # Pfade bestimmen
    destination_path = "merged_data"
    folder = Path(destination_path)
    folder.mkdir(parents=True, exist_ok=True)
    path_prefix = Path.cwd() / "cleaned_data"
    path_destination_prefix = Path.cwd() / destination_path

    # Erstellen der verschmolzenen Tabellen
    create_merged_table_orders(path_prefix, path_destination_prefix)

def create_merged_table_orders(path_prefix, path_destination_prefix):
    review_answer_timestamp_variable = "review_answer_timestamp"
    order_id_variable = "order_id"
    
    # parquet-Dateien holen
    df_orders = pd.read_parquet(path_prefix / "orders.parquet")
    df_customers = pd.read_parquet(path_prefix / "customers.parquet")
    df_reviews = pd.read_parquet(path_prefix / "reviews.parquet")
    
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

#def create_merged_table_products(path_prefix, path_destination_prefix):
    #df_orders = pd.read_parquet(path_prefix / "orders.parquet")
    #df_items = pd.read_parquet(path_prefix / "items.parquet")
    #df_sellers = pd.read_parquet(path_prefix / "sellers.parquet")