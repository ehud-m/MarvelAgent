import pandas as pd
from datasets import load_dataset
import ast
import itertools
import string


def excel_style_gene_names():
    for r in itertools.count(1):
        for letters in itertools.product(string.ascii_uppercase, repeat=r):
            yield ''.join(letters)


def build_marvel_dataframe():
    dataset = load_dataset("jrtec/Superheroes")
    df = pd.concat([dataset['train'].to_pandas(), dataset['test'].to_pandas()])
    df = df[df['creator'].notna()]  # Remove rows with missing creator
    marvel_df = df[df['creator'].str.lower().str.contains("marvel")].reset_index().copy(deep=True)

    marvel_df["superpowers"] = marvel_df["superpowers"].apply(ast.literal_eval)
    marvel_df["teams"] = marvel_df["teams"].apply(ast.literal_eval)

    unique_superpowers = {sp for lst in marvel_df["superpowers"] if isinstance(lst, list) for sp in lst}
    gene_name_generator = excel_style_gene_names()
    superpower_gene_mapping = {sp: f"Gene {next(gene_name_generator)}" for sp in unique_superpowers}

    marvel_df["Genes"] = marvel_df["superpowers"].apply(
        lambda powers: [superpower_gene_mapping[p] for p in powers]
    )

    reduced_marvel_df = marvel_df[["name", "history_text", "superpowers", "teams", "Genes"]].copy(deep=True)
    reduced_marvel_df.rename(
        columns={'name': 'Character Name', 'history_text': 'Description', 'superpowers': 'Primary Powers',
                 'teams': 'Affiliation'}, inplace=True)
    return reduced_marvel_df, superpower_gene_mapping
