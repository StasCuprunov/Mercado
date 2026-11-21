import pandas as pd
import plotly.express as px
import importlib

import style

importlib.reload(style)

from style import PASTELL

first_color = PASTELL.layout.colorway[0]

def analyze_sales_volume_from_sellers():
    seller_ids = draw_sales_volume_per_seller_id()
    sales_volume_for_seller_per_product_category(seller_ids)

def analyze_sales_volume_per_state():
    draw_sales_volume_per_seller_state()
    draw_sales_volume_per_state_per_product_category()

def analyze_sales_volume_per_product_id():
    draw_sales_volume_per_product_id()

def analyze_sales_volume_per_category():
    draw_sales_volume_per_category()
    draw_heat_map_for_product_and_product_category()

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
            sales_volume_variable: "Gesamtumsatz in BRL",
        }
    )
    
    # Passend zeichnen, so dass man komplett den höchsten Umsatzwert sehen kann
    fig.update_yaxes(range=[0, df_top[sales_volume_variable].max() * 1.1])
    fig.update_layout(template=PASTELL)
    fig.update_traces(marker_color=first_color)
    
    fig.show()

    seller_ids = df_top["seller_id"].dropna().unique().tolist()

    return seller_ids

def sales_volume_for_seller_per_product_category(seller_ids):
    seller_id_variable = "seller_id"
    sales_volume_variable = "sales_volume"
    product_category_name_variable = "product_category_name"
    
    df = pd.read_parquet("merged_data/merged_products_table.parquet")

    sales_volume = (
    df.loc[df[seller_id_variable].isin(seller_ids)]
      .assign(
          sales_volume=lambda d: d["price"] + d["freight_value"],
          product_category_name=lambda d: (
              d[product_category_name_variable].fillna("Ohne Kategorie")
          ),
      )
      .groupby([seller_id_variable, product_category_name_variable], as_index=False)
      .agg(sales_volume=(sales_volume_variable, "sum"))
    )

    fig = px.bar(
        sales_volume,
        x=sales_volume_variable,
        y=seller_id_variable,
        color=product_category_name_variable,
        color_discrete_sequence=px.colors.qualitative.Plotly,
        orientation="h",
        barmode="stack",
        template=PASTELL,
        title="Umsatz nach Verkäufer und Produktkategorie",
        labels={
            sales_volume_variable: "Gesamtumsatz in BRL inkl. Versand",
            seller_id_variable: "Verkäufer-ID",
            "product_category_name": "Produktkategorie",
        },
    )
    fig.update_yaxes(categoryorder="total ascending")
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

    fig.update_layout(template=PASTELL)
    fig.update_traces(marker_color=first_color)
    
    fig.show()

def draw_sales_volume_per_state_per_product_category():
    df = pd.read_parquet("merged_data/merged_products_table.parquet")

    umsatz_pro_staat = (
    df.assign(
        umsatz=lambda d: d["price"] + d["freight_value"],
        product_category_name=lambda d: (
            d["product_category_name"].astype("string").fillna("Ohne Kategorie")
        ),
    )
        .groupby(["seller_state", "product_category_name"], as_index=False)
        .agg(gesamtumsatz=("umsatz", "sum"))
    )

    fig = px.bar(
        umsatz_pro_staat,
        x="gesamtumsatz",
        y="seller_state",
        color="product_category_name",
        orientation="h",
        barmode="stack", 
        color_discrete_sequence=px.colors.qualitative.Plotly,
        template=PASTELL,
        title="Umsatz nach Verkäufer-Bundesstaat und Produktkategorie",
        labels={
            "gesamtumsatz": "Gesamtumsatz in BRL inkl. Versand",
            "seller_state": "Bundesstaat des Verkäufers",
            "product_category_name": "Produktkategorie",
        },
    )
    fig.update_yaxes(categoryorder="total ascending")
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

    products = volume_per_product.nlargest(top_number, sales_volume_variable).sort_values(sales_volume_variable, ascending=False)
    
    # Zeichnen von Top top_number höchsten Gesamtumsätze von Produkten
    fig = px.bar(
        products,
        x=product_id_variable,
        y=sales_volume_variable,
        title=f"Gesamtumsatz der Top {top_number} pro Produkt aus Frachtkosten und Preis",
        labels={product_id_variable: "Produkt-ID", sales_volume_variable: "Gesamtsumme in BRL"},
    )
    fig.update_layout(template=PASTELL)
    fig.update_traces(marker_color=first_color)
    
    fig.show()

    draw_number_orders_per_product(top_number, products)

def draw_number_orders_per_product(top_number, products):
    df = pd.read_parquet("merged_data/merged_products_table.parquet")
    
    product_id_variable = "product_id"
    number_orders_variable = "number_orders"
    
    orders_per_product = (
    df[product_id_variable]
      .value_counts()
      .rename_axis(product_id_variable)
      .reset_index(name=number_orders_variable)
    )
    
    fig = px.bar(
        orders_per_product.head(top_number),
        x=number_orders_variable,
        y=product_id_variable,
        orientation="h",
        title=f"Die {top_number} meistbestellten Produkte",
        labels={
            number_orders_variable: "Anzahl Bestellungen",
            product_id_variable: "Produkt-ID",
        },
        template=PASTELL,
        color_discrete_sequence=[first_color],
    )
    
    fig.update_yaxes(autorange="reversed")
    fig.show()
    
    same_product_ids = (
    products.loc[
        products[product_id_variable].isin(orders_per_product.head(top_number)[product_id_variable]),
        product_id_variable,
    ]
    .drop_duplicates()
    .tolist()
    )

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
        title=f"Gesamtumsatz der Top {top_number} Produktkategorien",
        labels={
            product_category_name_variable: "Produktkategorie",
            sales_volume_variable: "Gesamtumsatz in BRL",
        },
    )
    fig.update_layout(template=PASTELL)
    fig.update_traces(marker_color=first_color)
    
    fig.show()

def draw_heat_map_for_product_and_product_category():
    minimum_number = 250
    product_category_name_variable = "product_category_name"
    product_id_variable = "product_id"
    
    df = pd.read_parquet("merged_data/merged_products_table.parquet")
    orders = (
        df.assign(
            product_category_name=df[product_category_name_variable]
            .astype("string")
            .fillna("Ohne Kategorie")
        )
        .groupby([product_category_name_variable, product_id_variable], observed=True)["order_id"]
        .nunique()
    )
    
    heatmap = orders[orders > minimum_number].unstack(product_id_variable)
    
    fig = px.imshow(
        heatmap,
        aspect="auto",
        template=PASTELL,
        color_continuous_scale=["#FFFFFF", first_color],
        labels={
            "x": "Produkt-ID",
            "y": "Produktkategorie",
            "color": "Anzahl Bestellungen",
        },
        title=f"Bestellungen nach Produktkategorie und Produkt mit mindestens {minimum_number} Bestellungen",
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
    fig.update_layout(template=PASTELL)
    fig.update_traces(line_color=first_color)

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
            sales_volume_variable: "Gesamtumsatz in BRL"
        }
    )

    fig.update_layout(template=PASTELL)
    fig.update_traces(marker_color=first_color)
    
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

    fig.update_layout(template=PASTELL)
    fig.update_traces(marker_color=first_color)

    fig.show()
