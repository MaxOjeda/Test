import pandas as pd
import datetime
import emoji
import re
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=r"C:\Users\Max\Desktop\IMFD\constitucion-20210416-2b81735bc92e.json"

def month_convert(month_number):
    month = datetime.date(1900, month_number, 1).strftime('%b')
    return month


def parse_date(row):
    ''' función que setea el tiempo a 00:00:00 para distinguir y 
    formular topicos por día'''
    row = row.replace(hour=0, minute=0, second=0)
    return row


def clean_text(df):
    # eliminacion de etiquetas y hashtags
    df['text'] = df['text'].map(lambda x: re.sub(
        "(@[A-Za-z0-9-á-é-í-ó-ú]+)|(#[A-Za-z0-9-á-é-í-ó-ú]+)|(\w+:\/\/\S+)", ' ', str(x)))
    # eliminación de caracteres especiales
    df['text'] = df['text'].map(
        lambda x: re.sub('[,.¿¡!?_�@|#:]', ' ', str(x)))
    df['text'] = df['text'].map(lambda x: re.sub('[\']', ' ', str(x)))
    df['text'] = df['text'].map(lambda x: re.sub('[\/]', ' ', str(x)))
    df['text'] = df['text'].map(lambda x: re.sub('[+]', ' ', str(x)))
    # eliminar emoticones
    df['text'] = df['text'].map(lambda x: re.sub('(<[\w.%+->]+)', ' ', str(x)))
    df['text'] = df['text'].map(lambda x: re.sub('[\d]', ' ', str(x)))
    # todo a minusculas
    df['text'] = df['text'].map(lambda x: x.lower())

    return df


def deEmojify(text):
    return emoji.get_emoji_regexp().sub(r' ', text)


def filter_bots(data, data_bots):
    df_bots = pd.DataFrame()
    df_bots = data[data.user_id.isin(data_bots)]
    return df_bots


def filter_nobots(data, data_bots):
    df_nobots = pd.DataFrame()
    df_nobots = data[~data.user_id.isin(data_bots)]
    return df_nobots


def clean_dataset(PROJECT_ID, month_number, year_number):
    # fecha string
    mes = '%' + str(month_convert(month_number)) + '%'
    year = '%' + str(year_number) + '%'

    # primero cargamos los datos del mes
    bq_table_tw = 'constitucion-20210416.master.tw-streaming'
    query_tw = f"SELECT user.id AS user_id, created_at AS date, text FROM `{bq_table_tw}` WHERE created_at LIKE '{mes}' AND created_at LIKE '{year}' AND text NOT LIKE '%RT %' LIMIT 40000"
    data = pd.read_gbq(query_tw, project_id=PROJECT_ID, dialect='standard')

    # Limpiamos los datos: formato fecha, todo a minúscula, sacamos menciones y emojis (esto afecta la proporcion final)
    data['date'] = data['date'].astype('datetime64[ns]')
    data['date'] = data['date'].map(parse_date)  # formato de la fecha
    data = data[['user_id', 'date', 'text']
                ].sort_values(['date'], ascending=True)

    data = clean_text(data)
    data['text'] = data['text'].map(lambda x: deEmojify(x))

    # Cargamos datos de cuentas e info de bots
    df_bots_aux = pd.read_csv('temp/resultado_pegabot.csv',  sep=',')
    df_bots_aux = df_bots_aux.loc[df_bots_aux.loc[:,
                                                  'Resultado > 70%'] == 'Alta']

    # Separamos info de cuentass bots y no bots
    bots = filter_bots(data, df_bots_aux['ID do Usuário'])
    sin_bots = filter_nobots(data, df_bots_aux['ID do Usuário'])
    return bots, sin_bots
