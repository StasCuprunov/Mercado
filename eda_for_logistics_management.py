import pandas as pd
import plotly.express as px

def draw_sales_volume_per_seller_id():
    """ Gibt die top_number höchsten Umsätze als Balkendiagramm an
    """
    top_number = 20 # Wie viele der seller_ids sollen angezeigt werden
    seller_id_variable = "seller_id"
    sales_volume_variable = "sales_volume"

    # Einlesen
    df = pd.read_parquet("merged_data/merged_products_table.parquet")

    # Die top_number höchsten Umsätze pro seller_id filtern
    df_top = (
        df.drop_duplicates(subset=seller_id_variable)
        .sort_values(sales_volume_variable, ascending=False)
        .head(top_number)
        .copy()
    )

    # Zeichnen
    fig = px.bar(
        df_top,
        x=seller_id_variable,
        y=sales_volume_variable,
        title=f"Top {top_number} Verkäufer nach Gesamtumsatz",
        labels={
            seller_id_variable: "Verkäufer-ID",
            sales_volume_variable: "Gesamtumsatz",
        },
    )
    
    # Passend zeichnen, so dass man komplett den höchsten Umsatzwert sehen kann
    fig.update_yaxes(range=[0, df_top[sales_volume_variable].max() * 1.1])
    
    fig.show()

def draw_sales_volume_per_seller_state():
    """ Zeichne als logarithmierte Balkendiagramm den Gesamtumsatz je Bundesstaat
    """
    seller_state_variable = "seller_state"
    sales_volume_per_state_variable = "sales_volumen_per_state"
    sales_volume_variable = "sales_volume"

    # Einlesen
    df = pd.read_parquet("merged_data/merged_products_table.parquet")

    # Pro Bundesstaat den Gesamtumsatz über alle Verkäufer berechnen
    sales_per_state = (
        df
        .groupby(seller_state_variable, as_index=False)[sales_volume_variable]
        .sum()
        .rename(columns={sales_volume_variable: sales_volume_per_state_variable})
        .sort_values(sales_volume_per_state_variable, ascending=False)
        .reset_index(drop=True)
    )

    # Zeichnen
    fig = px.bar(
        sales_per_state.sort_values(sales_volume_per_state_variable, ascending=False),
        x=seller_state_variable,
        y=sales_volume_per_state_variable,
        title="Gesamtumsatz pro Bundesstaat",
        labels={seller_state_variable: "Bundesstaat", sales_volume_per_state_variable: "Gesamtumsatz in BRL - logarithmisch"},
        log_y=True
    )
    
    fig.show()

def draw_sales_volume_per_product_id():
    """ Zeichne als Balkendiagramm den Gesamtumsatz pro Produkt
    """
    top_number = 20
    product_id_variable = "product_id"
    sales_volume_variable = "sales_volume"
    
    # Einlesen
    df = pd.read_parquet("merged_data/merged_products_table.parquet")
    
    # Pro Produkt Gesamtumsatz berechnen und als Variable "sales_volume" speichern
    volume_per_product = (
        df.assign(sales_volume=df["price"] + df["freight_value"])
        .groupby(product_id_variable, as_index=False)[sales_volume_variable]
        .sum()
    )
    
    # Zeichnen von Top top_number höchsten Gesamtumsätze von Produkten
    fig = px.bar(
        volume_per_product.nlargest(top_number, sales_volume_variable).sort_values(sales_volume_variable, ascending=False),
        x=product_id_variable,
        y=sales_volume_variable,
        title=f"Gesamtumsatz der Top {top_number} pro Produkt aus Frachtkosten und Preis",
        labels={product_id_variable: "Produkt-ID", sales_volume_variable: "Gesamtsumme in BRL"},
    )
    
    fig.show()

def draw_sales_volume_per_customer_id():
    """ Zeichen die top_number Gesamtumsätze pro Kunde
    """
    top_number = 20
    customer_id_variable = "customer_id"
    total_value_variable = "total_value"
    
    # Einlesen
    df = pd.read_parquet("merged_data/merged_orders_table.parquet")
    
    # Umsatz pro Kunde bestimmen
    sales_volume_per_customer = (
        df.groupby(customer_id_variable, as_index=False)[total_value_variable]
        .sum()
        .sort_values(total_value_variable, ascending=False)
    )

    # Zeichnen
    fig = px.bar(
        sales_volume_per_customer.head(top_number),
        x=customer_id_variable,
        y=total_value_variable,
        title="Gesamtumsatz pro Kunde",
        labels={customer_id_variable: "Kunden-ID", total_value_variable: "Gesamtumsatz in BRL"},
    )
    
    fig.show()

def draw_sales_volume_per_category():
    """ Die top_number Kategorien im Bezug auf Gesamtumsatz als Balkendiagramm zeichnen
    """
    top_number = 20
    sales_volume_variable = "sales_volume"
    product_category_name_variable = "product_category_name"

    # Einlesen
    df = pd.read_parquet("merged_data/merged_products_table.parquet")

    # Pro Kategorie dessen Umsatz aus Preis und Frachtkosten berechnen
    sales_volume_per_category = (
        df.assign(sales_volume=df["price"] + df["freight_value"])
        .groupby(product_category_name_variable, as_index=False)[sales_volume_variable]
        .sum()
        .sort_values(sales_volume_variable, ascending=False)
        .reset_index(drop=True)
    )

    # Zeichnen der top_number Kategorien
    fig = px.bar(
        sales_volume_per_category.nlargest(top_number, sales_volume_variable),
        x=product_category_name_variable,
        y=sales_volume_variable,
        title="Gesamtumsatz pro Produktkategorie",
        labels={
            product_category_name_variable: "Produktkategorie",
            sales_volume_variable: "Gesamtumsatz in BRL",
        },
    )
    
    fig.show()