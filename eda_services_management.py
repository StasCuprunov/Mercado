import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_box_plots_for_reviews():
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

    