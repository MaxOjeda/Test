from dictionary import get_dictionary
from download import clean_dataset
from processing import emotion_processing, stream_emotions
from connect_GCP.bigquery.upload import upload_file_to_bucket
from connect_GCP.storage.download import download_blob

PROJECT_ID = 'constitucion-20210416'

def emotions_analysis(month, year=2021, n_emotions=4):

    download_blob("data_connections", "emotions/resultado_pegabot.csv",
                  "temp/resultado_pegabot.csv")
    download_blob("data_connections", "emotions/spanish-emotion-intensity-lexicon.txt",
                  "temp/spanish-emotion-intensity-lexicon.txt")

    dictionary = get_dictionary('temp/spanish-emotion-intensity-lexicon.txt')
    bots, sin_bots = clean_dataset(PROJECT_ID, month, year)
    df_sin_bots = emotion_processing(sin_bots, dictionary)
    df_bots = emotion_processing(bots, dictionary)
    stream_emotions('Emociones En Twitter', 'Principales Emociones En Twitter', 'html_all_emociones_sin_bots.html',
                    'html_top_emociones_sin_bots.html', dictionary, df_sin_bots, n_emotions)
    stream_emotions('Emociones De Los Bots', 'Principales Emociones De Los Bots', 'html_all_emociones_bots.html',
                    'html_top_emociones_bots.html', dictionary, df_bots, n_emotions)

    upload_file_to_bucket(
        "data_connections", "html_top_emociones_bots.html", "emotions/top_bots_emotions.html"
    )
    upload_file_to_bucket(
        "data_connections", "html_top_emociones_sin_bots.html", "emotions/top_sin_bots_emotions.html"
    )

emotions_analysis(9)