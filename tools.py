from __future__ import annotations
"""import io
import os
import re
import json
import openai
import pickle
import asyncio
import pandas as pd
import datetime as dt
from pprint import pprint
from tqdm.auto import tqdm
from pydantic import BaseModel 
from bs4 import BeautifulSoup as bs
from openai.types import VectorStore
from agents import set_default_openai_key, set_tracing_export_api_key, trace
from agents import Agent, Runner, ModelSettings, FileSearchTool
from EdgarCache.Client.Client import Client as EdgarCacheClient"""


#TODO: EdgarCache Client should be a singleton, VectorStore helpers
#Anything that is not LLM reasoning but is required by every agent should be here


"""provider = 'openai'
user = 'CACS'
with open('//fs1/shares/dept/trading/specialsituations/Working/MARIO/AI/data/keys.json', 'r') as f:
    creds = json.load(f).get(provider)
    env_var = creds.get('env_var')
    key = creds.get('keys').get(user)
    os.environ[env_var]=key
    if provider == 'openai':
        set_default_openai_key(os.getenv(env_var))
        set_tracing_export_api_key(os.getenv(env_var))
        OpenAI_CLIENT = openai.OpenAI(api_key=key)

class VectorStoreItem:
	def __init__(self, content, url, name):
		self.content = content
		self.url = url
		self.name = name

	def asFile(self):
		class NamedBytesIO(io.BytesIO):
			def __init__(self, name, *args, **kwargs):
				super().__init__(*args, **kwargs)
				self.name = name

		file = NamedBytesIO(self.name)
		file.write(self.content)
		file.seek(0)

		return file
     
def format_for_openai(url:str) -> str:
    if url.endswith('.htm'):
        return url.replace('.htm', '.html')
    else:
        return url
    
def create_vector_store(edgarCache, name:str, urls: list[str]) -> VectorStore:
    vector_store = OpenAI_CLIENT.vector_stores.create(name=name)
    files = [VectorStoreItem(edgarCache.Get(url).content, url, format_for_openai(url)).asFile() for url in urls]
    file_batch = OpenAI_CLIENT.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=files
    )
    return vector_store"""


# balancesheet/tools.py
"""
Pure-Python I/O helpers: EDGAR cache client, vector-store upload,
file search tool wrapper, HTML utils, etc.
"""



import io
import os
import re
import datetime as dt
from datetime import date
from typing import Iterable, List

import bs4
import openai
from openai.types import VectorStore

from agents import FileSearchTool  # ← your wrapper from the prototype
from EdgarCache.Client.Client import Client as EdgarCacheClient
from EdgarCache.Sec.Submissions import Submission, Submissions
from models import FullBalanceSheet
from settings import get_openai_client  # ← your OpenAI client from settings.py

# ---------------------------------------------------------------------------
# 1.  VectorStore helpers
# ---------------------------------------------------------------------------

class _VectorStoreItem:
    """
    Wraps raw bytes + name to satisfy openai.vector_stores.file_batches.upload
    which expects a file-like object with .name attr.
    """
    def __init__(self, content: bytes, url: str):
        self.content = content
        self.url     = url
        self.name    = self._format_for_openai(url)

    def _format_for_openai(self, url: str) -> str:
        return url.replace('.htm', '.html') if url.endswith('.htm') else url

    def as_file(self) -> io.BytesIO:
        buf      = io.BytesIO(self.content)
        buf.name = self.name
        buf.seek(0)
        return buf


def format_for_openai(url:str) -> str:
    if url.endswith('.htm'):
        return url.replace('.htm', '.html')
    else:
        return url



def create_vector_store(
        ec: EdgarCacheClient,
        name: str,
        urls: Iterable[str],
        client: openai.OpenAI | None = None
) -> VectorStore:
    """
    1. downloads each URL via EdgarCache
    2. creates an OpenAI vector-store
    3. uploads all documents and blocks until ready
    """
    client = client or get_openai_client()
    vs = client.vector_stores.create(name=name)

    tmp = []
    for u in urls:
        if not u.endswith('.xsd') and not u.endswith('.xml') and not u.endswith('.jpg') and not u.endswith('.gif'):
            tmp.append(u)
    urls = tmp

    files = []
    for u in urls:
        content = ec.Get(u).content
        if content:
            files.append(_VectorStoreItem(content, u).as_file())
    if not files:
        raise ValueError(f"No valid files found in URLs: {urls}")
    client.vector_stores.file_batches.upload_and_poll(vector_store_id=vs.id,
                                                      files=files)
    return vs

def create_vector_store_for_updates(
        ec: EdgarCacheClient,
        name: str,
        urls: Iterable[str],
        client: openai.OpenAI | None = None
) -> VectorStore:
    """
    1. downloads each URL via EdgarCache
    2. creates an OpenAI vector-store
    3. uploads all documents and blocks until ready
    """
    client = client or get_openai_client()
    vs = client.vector_stores.create(name=name)

    tmp = []
    for sublist in urls:
        for u in sublist:
            if not u.endswith('.xsd') and not u.endswith('.xml') and not u.endswith('.jpg') and not u.endswith('.gif'):
                tmp.append(u)
    urls = tmp

    files = []
    for u in urls:
        content = ec.Get(u).content
        if content:
            files.append(_VectorStoreItem(content, u).as_file())
    if not files:
        raise ValueError(f"No valid files found in URLs: {urls}")
    client.vector_stores.file_batches.upload_and_poll(vector_store_id=vs.id,
                                                      files=files)
    return vs



# ---------------------------------------------------------------------------
# 2.  EDGAR index parsing
# ---------------------------------------------------------------------------

_SEC_PREFIX = 'https://www.sec.gov'


def extract_doc_urls(index_html: bytes) -> List[str]:
    """
    Takes the .html ‘index’ file that EDGAR serves and extracts
    the individual document links (.htm, .html, .xml).
    """
    soup = bs4.BeautifulSoup(index_html, 'lxml')
    hrefs = [a['href'] for a in soup.select('a[href$=".htm"], a[href$=".html"]')]
    return [
        h if h.startswith('http') else _SEC_PREFIX + h
        for h in hrefs
    ]


# ---------------------------------------------------------------------------
# 3.  Quick-n-dirty text scraper (optional)
# ---------------------------------------------------------------------------

def get_plain_text(html: bytes) -> str:
    return bs4.BeautifulSoup(html, 'lxml').get_text(' ', strip=True)


# ---------------------------------------------------------------------------
# 4.  Build a FileSearchTool in one line
# ---------------------------------------------------------------------------

def make_file_search_tool(vs_id: str, max_k: int = 12) -> FileSearchTool:
    return FileSearchTool(
        max_num_results=max_k,
        vector_store_ids=[vs_id],
        include_search_results=False
    )

def get_all_sub_filings(client: EdgarCacheClient, cik: int, start: dt.date = dt.date(2000, 1, 1)) -> List[str]:
    """
    Returns a list of all filings for a given CIK after a given date.
    """
    submissions: dict[str,Submission]=Submissions.load(client=client,cik=cik,formFilter=None,start=start).items

    urls = []
    for sub in submissions.values():
        urls.append(sub.getLink())
    return urls

