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
    """ Zeichne als logarithmierte Punktdiagramm den Gesamtumsatz je Bundesstaat
    """
    seller_state_variable = "seller_state"
    sales_volume_per_state_variable = "sales_volume_per_state"
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
    fig = px.scatter(
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
    sales_volume_variable = "sales_volume"
    
    # Einlesen
    df = pd.read_parquet("merged_data/merged_orders_table.parquet")
    
    # Umsatz pro Kunde bestimmen
    df[sales_volume_variable] = df["total_value"] + df["total_freight_cost"]
    
    sales_volume_per_customer = (
        df.groupby(customer_id_variable, as_index=False)[sales_volume_variable]
        .sum()
        .sort_values(sales_volume_variable, ascending=False)
    )

    # Zeichnen
    fig = px.bar(
        sales_volume_per_customer.head(top_number),
        x=customer_id_variable,
        y=sales_volume_variable,
        title="Gesamtumsatz pro Kunde",
        labels={customer_id_variable: "Kunden-ID", sales_volume_variable: "Gesamtumsatz in BRL"},
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

def draw_sales_volume_per_month():
    """ Zeitlicher Verlauf von Gesamtumsatz von Mercado pro Monat

    """
    date_variable = "order_delivered_customer_date"
    sales_volume_per_order_variable = "sales_volume_per_order"

    # Einlesen
    df = pd.read_parquet("merged_data/merged_orders_table.parquet")
    
    df[date_variable] = pd.to_datetime(df[date_variable])
    
    # Gesamtmumsatz per Bestellung berechnen
    df[sales_volume_per_order_variable] = df["total_value"] + df["total_freight_cost"]

    # Monatlicher Gesamtumsatz berechnen
    monthly_sales = (
        df.groupby(pd.Grouper(key=date_variable, freq="MS"))[sales_volume_per_order_variable]
        .sum()
        .reset_index()
    )

    # Zeichnen
    fig = px.line(
        monthly_sales,
        x=date_variable,
        y=sales_volume_per_order_variable,
        markers=True,
        title="Monatlicher Gesamtumsatz aller Bestellungen",
        labels={
            date_variable: "Monat",
            sales_volume_per_order_variable: "Gesamtumsatz in BRL"
        }
    )

    fig.show()

def connection_between_sales_volume_and_number_of_photos():
    """ Zusammenhang zwischen Anzahl Produktfotos und Umsatz vom Produkt herausfinden
    """
    sales_volume_variable = "sales_volume"
    number_photos_variable = "number_photos"
    product_id_variable = "product_id"
    number_products_variable = "number_products"

    # Einlesen
    df = pd.read_parquet("merged_data/merged_products_table.parquet")

    # Spearman-Korrelationskoeffizienten bestimmen
    
    # Gesamtpreis berechnen
    df[sales_volume_variable] = df["price"] + df["freight_value"]

    # Pro Produkt Anzahl Fotos und dessen Gesamtumsatz bestimmen
    sales_per_product = (
        df.groupby(product_id_variable, as_index=False)
        .agg(
            number_photos=("product_photos_qty", "first"),
            sales_volume=(sales_volume_variable, "sum")
        )
        .dropna(subset=[number_photos_variable, sales_volume_variable])
    )

    # Zeichnen
    fig = px.scatter(
        sales_per_product,
        x=number_photos_variable,
        y=sales_volume_variable,
        hover_data=[product_id_variable],
        title="Zusammenhang zwischen Produktfotos und Umsatz",
        labels={
            number_photos_variable: "Anzahl Produktfotos",
            sales_volume_variable: "Gesamtumsatz inklusive Versandkosten in BRL"
        }
    )
    
    fig.show()
    
    # Spearman-Korrelation bestimmen
    correlation = sales_per_product[number_photos_variable].corr(
        sales_per_product[sales_volume_variable],
        method="spearman"
    )
    
    print(f"Spearman-Korrelation: {correlation:.3f}")

    # Zeichnen von Anzahl Fotos in Abhängigkeit von Anzahl Produkten
    products_per_number_photos = (
        sales_per_product.groupby(number_photos_variable)
        .size()
        .reset_index(name=number_products_variable)
        .sort_values(number_photos_variable)
    )

    # Zeichnen
    fig = px.bar(
        products_per_number_photos,
        x=number_photos_variable,
        y=number_products_variable,
        title="Anzahl Produkte nach Anzahl der Produktfotos",
        labels={
            number_photos_variable: "Anzahl Fotos",
            number_products_variable: "Anzahl Produkte"
        }
    )

    fig.show()
