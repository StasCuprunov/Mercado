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