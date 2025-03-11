import pandas as pd
import shutil

from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma

import kagglehub
from kagglehub import KaggleDatasetAdapter

import gradio as gr


def load_frame_from_kaggle():
    df = kagglehub.load_dataset(
        KaggleDatasetAdapter.PANDAS,
        "tedcoderman/pathfinder-1e-feats-and-benefits",
        "feats_clean.csv"
    )
    return df


def load_documents_from_kaggle():
    data = kagglehub.dataset_download("tedcoderman/pathfinder-1e-feats-and-benefits", path='tagged_benefit.txt')
    shutil.copyfile(data, 'tagged_benefit.txt')
    raw_documents = TextLoader('tagged_benefit.txt').load()
    splitter = CharacterTextSplitter(separator="\n", chunk_size=0, chunk_overlap=0)
    documents = splitter.split_documents(raw_documents)
    return documents


def load(loaded: bool = False, persist: bool = True):
    feats_df = load_frame_from_kaggle()
    if loaded:
        feats_db = Chroma(persist_directory="./db", embedding_function=GPT4AllEmbeddings())
    else:
        documents = load_documents_from_kaggle()
        feats_db = Chroma().from_documents(documents, embedding=GPT4AllEmbeddings(), persist_directory='./db' if persist else None)

    return (feats_df, feats_db)


def similarity_search(feats_db, query: str, top_k: int = 50) -> list[int]:
    recs = feats_db.similarity_search(query, k=top_k)
    return [int(rec.page_content.split('|')[0].strip('"').strip()) for rec in recs]


def feats_to_markdown(feats_frame: pd.DataFrame) -> gr.Markdown:
    result = ""
    suffix = ''
    for i in range(len(feats_frame)):
        row = feats_frame.iloc[i]
        if type(row['Name']) is not  str and suffix == '':
            suffix = '_y'
            result += "\n\n## Feats not included in your selection\n\n-----\n\n"
        else:
            result += f"## {row['Name' + suffix]}\n\n### Prerequisites: {row['Prerequisites' + suffix]}\n\n**{row['Short Description' + suffix]}**\n\n{row['long_description' + suffix]}\n\n-----\n\n"

    return gr.Markdown(result)


def build_dashboard(feats_df, feats_db):
    def recommend_feats(query, books: list[str] = [], categories: list[str] = [], top_k: int = 10) -> gr.Markdown:
        feat_ids = similarity_search(feats_db, query)
        similar_feats = feats_df.filter(items=feat_ids, axis=0)
        results = pd.DataFrame()

        if len(books) > 0 and not (len(books) == 1 and books[0] == 'All'):
            # limit our results to matching books
            results = similar_feats[similar_feats['Books'].str.contains('|'.join(books), regex=True)]
        if len(categories) > 0 and not (len(categories) == 1 and categories[0] == 'All'):
            results = similar_feats[similar_feats['Category'].str.contains('|'.join(categories), regex=True)]

        if len(results) < top_k:
            results = results.merge(similar_feats, how='outer', left_index=True, right_index=True, indicator=True, suffixes=(None, '_y'))
            results = results.sort_values(by=['_merge'], ascending=False, ignore_index=True)

        results = results.head(top_k)

        return feats_to_markdown(results)

    books = [
        "All",
        "Core Rulebook",
        "Bestiary",
        "Advanced Class Guide",
        "Advanced Player's Guide",
        "Advanced Race Guide",
        "Monster Codex",
        "Mythic Adventures",
        "Occult Adventures",
        "Pathfinder Unchained",
        "Technology Guide",
        "Ultimate Campaign",
        "Ultimate Combat",
        "Ultimate Magic"
    ]
    categories = [
        "All",
        "Alignment",
        "Combat",
        "Critical",
        "Esoteric",
        "Grit",
        "Item Creation",
        "Metamagic",
        "Mythic",
        "Panache",
        "Performance",
        "Stare",
        "Story",
        "Style",
        "Teamwork"
    ]
    with gr.Blocks(theme = gr.themes.Soft()) as dashboard:
        gr.Markdown("# Pathfinder 1E Feat Recommender")

        with gr.Row():
            user_query = gr.Textbox(label = "Describe the feat you want:", placeholder="a bonus to perception checks")
            categories_dropdown = gr.Dropdown(choices = categories, label = 'Categories', value = "All", multiselect = True)
            books_dropdown = gr.Dropdown(choices = books, label = 'Books', value = "All", multiselect = True)
            submit_button = gr.Button("Give me Feat Ideas!")

        gr.Markdown("## Recommendations")
        output = gr.Markdown("")

        submit_button.click(fn = recommend_feats, inputs = [user_query, books_dropdown, categories_dropdown], outputs = output)

        return dashboard


if __name__ == '__main__':
    print('Loading Database...')
    frame, db = load(loaded=False, persist=False)
    print('Building Dashboard...')
    dashboard = build_dashboard(frame, db)
    print('Launching Dashboard...')
    dashboard.launch(server_port=5000)
