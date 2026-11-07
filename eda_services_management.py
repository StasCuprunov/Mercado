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