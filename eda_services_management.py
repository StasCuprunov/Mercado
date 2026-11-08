import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_box_plots_for_reviews():
    """ Zeichen Boxplot für alle Jahre für das Attribut Bewertung
    """
    review_answer_timestamp_variable = "review_answer_timestamp"
                                     
    df_reviews = pd.read_parquet("cleaned_data/reviews.parquet")

    # Umwandeln in Datum
    df_reviews[review_answer_timestamp_variable] = pd.to_datetime(df_reviews[review_answer_timestamp_variable])

    # Für die revelanten Jahre
    years = [year for year in range(2016, 2019, 1)]

    # Schlüssel-Wert-Paar mit Schlüssel gleich Jahr und Wert gleich DataFrame vom jeweiligen Jahr
    # Nur die neuesten Bewertungen werden berücksichtigt
    df_dictionary = {}
    for year in years:
        df_dictionary[year] = df_reviews.loc[df_reviews[review_answer_timestamp_variable].dt.year == year]
        df_dictionary[year] = (
            df_dictionary[year].sort_values("review_id")
                .drop_duplicates(subset=review_answer_timestamp_variable, keep="last")
        )

    # Zeichnen der Boxplots
    years = sorted(df_dictionary)
    
    fig = make_subplots(
        rows=1,
        cols=len(years),
        subplot_titles=[str(year) for year in years],
        shared_yaxes=True
    )

    # Pro Jahr ein Boxplot zeichnen
    for column, year in enumerate(years, start=1):
        fig.add_trace(
            go.Box(
                y=df_dictionary[year]["review_score"],
                name=str(year),
                boxmean=True
            ),
            row=1,
            col=column
        )
    
    fig.update_yaxes(range=[0.5, 5.5], dtick=1)
    fig.update_yaxes(title_text="Bewertung", row=1, col=1)
    fig.update_layout(title_text="Bewertungen pro Jahr", showlegend=False)
    
    fig.show()

def average_review_score_per_month():
    """ Zeichne pro Monat die durchschnittliche Bewertung

    """
    review_answer_timestamp_variable = "review_answer_timestamp"
    review_score_average_variable = "review_score_average"
    
    df = pd.read_parquet("cleaned_data/reviews.parquet")

    # Nur die letzten Bewertungen in Bedracht ziehen
    df = (
        df.sort_values("review_id")
            .drop_duplicates(subset=review_answer_timestamp_variable, keep="last")
    )
    
    # Umwandeln in Datum
    df[review_answer_timestamp_variable] = pd.to_datetime(df[review_answer_timestamp_variable])

    # Berechne die Durchschnittsbewertung pro Monat und sortiere nach chronologische Zeit
    average_per_month = (
        df.groupby(pd.Grouper(key=review_answer_timestamp_variable, freq="MS"))["review_score"]
          .mean()
          .reset_index(name=review_score_average_variable)
          .sort_values(review_answer_timestamp_variable)
    )

    # Zeichnen
    fig = px.line(
        average_per_month,
        x=review_answer_timestamp_variable,
        y=review_score_average_variable,
        markers=True,
        title="Durchschnittliche Bewertung pro Monat",
        labels={
            review_answer_timestamp_variable: "Monat",
            review_score_average_variable: "Durchschnittliche Bewertung"
        }
    )
    
    fig.update_xaxes(dtick="M1", tickformat="%m.%Y")
    fig.show()

def plot_number_of_bad_reviews_per_day():
    """ Zeichne pro Tag die Anzahl der schlechten Bewertungen
    """
    review_answer_timestamp_variable = "review_answer_timestamp"
    number_of_reviews_variable = "number_of_reviews"

    # Datei einlesen
    df = pd.read_parquet("cleaned_data/reviews.parquet")

    # Nur die letzten Bewertungen in Bedracht ziehen
    df = (
        df.sort_values("review_id")
            .drop_duplicates(subset=review_answer_timestamp_variable, keep="last")
    )

    # In Datum umwandeln
    df[review_answer_timestamp_variable] = pd.to_datetime(df[review_answer_timestamp_variable])

    # Zählt Anzahl schlechter Bewertungen pro Tag
    number_bad_reviews_per_day = (
        df.loc[df["review_score"] <= 2]
          .groupby(pd.Grouper(key=review_answer_timestamp_variable, freq="D"))
          .size()
          .reset_index(name=number_of_reviews_variable)
    )

    # Zeichnen
    fig = px.line(
        number_bad_reviews_per_day,
        x=review_answer_timestamp_variable,
        y=number_of_reviews_variable,
        title="Anzahl schlechte Bewertungen (<= 2) pro Tag",
        labels={
            review_answer_timestamp_variable: "Datum",
            number_of_reviews_variable: "Anzahl der Bewertungen"
        }
    )
    
    fig.update_yaxes(rangemode="tozero", dtick=1)
    fig.show()

def connection_between_delivery_quality_and_reviews():
    """ Zusammenhänge zwischen Lieferqualität und Bewertungen herausfinden
    """
    draw_devlivery_time_in_days_and_number_of_reviews_per_review_score()
    draw_delay_and_number_of_reviews_per_review_score()
    
def draw_devlivery_time_in_days_and_number_of_reviews_per_review_score():
    """ Zeichnen von Balkendiagramm mit Anzahl Bewertungen pro Bewertungswert nach Lieferdauergruppe

    """
    last_review_score_variable = "last_review_score"
    delivery_time_in_days_variable = "delivery_time_in_days"

    # Einlesen
    df = pd.read_parquet("merged_data/merged_orders_table.parquet")

    # Histogramm über Lieferdauergruppe und Anzahl dazugehörigen Bewertungen
    fig = px.histogram(
        df,
        x=last_review_score_variable,
        color=delivery_time_in_days_variable,
        barmode="group",
        category_orders={
            delivery_time_in_days_variable: [
                "<= 7", "8 to 14", "15 to 21", "> 21", "no value"
            ]
        },
        labels={
            last_review_score_variable: "Bewertung",
            delivery_time_in_days_variable: "Lieferzeit in Tagen"
        },
        title="Bewertungen nach Lieferzeit",
        template="plotly_white"
    )
    
    fig.update_traces(xbins=dict(start=0.5, end=5.5, size=1))
    fig.update_xaxes(dtick=1)
    fig.update_yaxes(title_text="Anzahl")
    fig.show()

def draw_delay_and_number_of_reviews_per_review_score():
    """ Zeichnen von Balkendiagramm mit Anzahl Verspätungen und dessen Bewertung
    """
    last_review_score_variable = "last_review_score"
    
    df = pd.read_parquet("merged_data/merged_orders_table.parquet")

    # Nur die verspäteten Zeilen nehmen
    df_delay = df.loc[df["delay"] == True]

    # Zeichnen
    fig = px.histogram(
        df_delay,
        x=last_review_score_variable,
        labels={last_review_score_variable: "Bewertung"},
        title="Anzahl verspäteter Lieferungen pro Bewertung",
        template="plotly_white"
    )
    
    fig.update_traces(
        xbins=dict(start=0.5, end=5.5, size=1),
        marker_color="#3498DB"
    )
    fig.update_layout(bargap=0.45)
    fig.update_xaxes(dtick=1)
    fig.update_yaxes(title_text="Anzahl verspäteter Lieferungen")
    fig.show()

def connection_betweeen_review_score_and_total_value():
    """ Zusammenhang zwischen Bewertungswert und Gesamtkosten herausfinden
    
    """

    last_review_score_variable = "last_review_score"
    total_value_variable = "total_value"

    # Daten einlesen
    df = pd.read_parquet("merged_data/merged_orders_table.parquet")

    # DataFrame fürs Zeichnen erstellen
    plot_df = df[
        [last_review_score_variable, total_value_variable]
    ].dropna()

    # Zeichnen
    fig = px.box(
        plot_df,
        x=last_review_score_variable,
        y=total_value_variable,
        points="outliers",
        labels={
            last_review_score_variable: "Bewertung",
            total_value_variable: "Gesamtkosten (BRL)"
        },
        title="Gesamtkosten nach Bewertung",
        template="plotly_white"
    )
    
    fig.update_xaxes(
        type="category",
        categoryorder="array",
        categoryarray=[1, 2, 3, 4, 5]
    )
    fig.update_traces(marker_color="#3498DB")
    fig.show()

    # Korrelation zwischen Gesamtpreis und Bewertung nach Spearman bestimmen
    korrelation = plot_df[total_value_variable].corr(
        plot_df[last_review_score_variable],
        method="spearman"
    )
    print(f"Spearman-Korrelation: {korrelation:.3f}")