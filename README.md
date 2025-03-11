# Pathfinder Feat Finder

> This is an LLM taught on Pathfinder 1st Edition Feats
> 
> All data pulled from https://legacy.aonprd.com

## Installation

If you want to run this yourself, you can pull down the docker image from [Dockerhub](https://hub.docker.com/repository/docker/deltreey/pathfinder-feat-finder/general).

```bash
docker run -p 5000:5000 deltreey/pathfinder-feat-finder
```

Then just open up your browser to http://localhost:5000

## Coding

If you want to work on the code, everything should be in this repository.  The data was scraped from
https://legacy.aonprd.com using `wget --mirror --convert-links --adjust-extension --page-requisites --no-parent` which
didn't perfectly replace all the links, unfortunately.  All of that is in the `legacy.aonprd.com` directory.  There are
a few minor edits to those files that I had to make for ingestion.  The site has a lot of typos.

The scrape was then parsed into [pandas](https://pandas.pydata.org/) Dataframes using a series of
[Jupyter Notebooks](https://jupyter.org/).  Both the Notebooks and the resulting CSVs of the DataFrames are contained in
this repository.  For convenience, the CSV files are also uploaded to
[Kaggle](https://www.kaggle.com/datasets/tedcoderman/pathfinder-1e-feats-and-benefits).

Finally, I dumped the **Benefit** content from each feat's description into
[ChromaDB](https://docs.trychroma.com/docs/overview/introduction) and wired it up with
[GPT4All](https://github.com/nomic-ai/gpt4all).  The result is that you can use plaintext to search for feats with
the benefits you want.

To make it easy to use, I am using [Gradio](https://www.gradio.app/) to create a webpage where you can select which
books/categories of feats you want before searching.  The code for this is in `dashboard.py`.

And to make it easy to deploy, I dockerized it, and the Dockerfile is contained in this repository.

If this looks familiar, it's because I followed [this tutorial](https://www.youtube.com/watch?v=Q7mS1VHm3Yw).

## Improvements

I have lots of things I'd like to do to improve this.

1. I'd like to find a way to handle prerequisites.  Many feats are race- or class-specific.  I'd like to make it easier
    for players to automatically exclude feats they're not qualified for (and never could be?)
2. I want to do more than just feats, though that may be better done with a separate LLM.
3. Potentially, it might be good to have a more persistent conversation about the feat selection, rather than a
    one-and-done search.
