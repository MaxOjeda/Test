import pandas as pd
import regex as re


def get_dictionary(filepath):

    # llamamos diccionario
    emolex_df = pd.read_csv(filepath,  names=[
                            "ingles", "español", "emocion", "valor"], skiprows=1, sep='\t', keep_default_na=False)

    # agregamos las mismas palabras del diccionario anterior, pero sin tildes (emolex modificado)
    tildes_min = str.maketrans('áéíóöúü', 'aeioouu')
    tildes_mayus = str.maketrans('ÁÉÍÓÖÚÜ', 'AEIOOUU')

    for _, row in emolex_df.iterrows():
        if re.search(r'[ÁÉÍÓÚáéíóúÜü]', row.español):
            palabra = row.español
            palabra = palabra.translate(tildes_min)
            palabra = palabra.translate(tildes_mayus)
            new_word = {'ingles': row.ingles, 'español': palabra,
                        'emocion': row.emocion, 'valor': row.valor}
            emolex_df = emolex_df.append(new_word, ignore_index=True)
    return emolex_df
