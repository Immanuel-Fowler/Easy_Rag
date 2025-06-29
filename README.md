# Easy_Rag

Easy_Rag is a Streamlit-based application for building, updating, and querying Retrieval-Augmented Generation (RAG) databases using various embedding models and data sources. It provides a user-friendly interface for managing vector databases, uploading data from sitemaps, web pages, and (soon) PDFs, and interacting with a chatbot powered by LLMs.

## Features

- **Database Management:** Create and manage multiple vector databases.
- **Collection Management:** Add collections with different embedding models.
- **Data Ingestion:** Upload data from sitemaps, web pages, and (coming soon) PDF files.
- **RAG Chatbot:** Query your data using a conversational interface.
- **Drag-and-Drop Flow Builder:** Visualize and design RAG pipelines (experimental, via Barfi).
- **Remove Data by Source:** Easily remove documents from collections by their source.

## Project Structure

```
main.py
pages/
    drag and drop.py
    invoke chatbot.py
    test.py
.gitignore
```

- `main.py`: Main dashboard for database and collection management, data ingestion, and removal.
- `pages/invoke chatbot.py`: Chatbot interface for querying your data.
- `pages/drag and drop.py`: Visual flow builder for RAG pipelines (Barfi integration).
- `pages/test.py`: Utility script for listing available databases.

## Getting Started

### Prerequisites

- Python 3.8+
- [Streamlit](https://streamlit.io/)
- [chromadb](https://www.trychroma.com/)
- [langchain](https://python.langchain.com/)
- [barfi](https://github.com/ericmjl/barfi) (for flow builder)
- Other dependencies as required (see below)

### Installation

1. Clone this repository:

    ```sh
    git clone https://github.com/yourusername/Easy_Rag.git
    cd Easy_Rag
    ```

2. Install dependencies:

    ```sh
    pip install -r requirements.txt
    ```

    *(Create a `requirements.txt` with the necessary packages if not present.)*

3. Run the app:

    ```sh
    streamlit run main.py
    ```

4. Access the app in your browser at `http://localhost:8501`.

## Usage

- **Create a Database:** Use the main dashboard to create a new database.
- **Add Collections:** Assign embedding models to collections.
- **Ingest Data:** Upload data from sitemaps or web pages.
- **Query Data:** Use the chatbot interface to ask questions about your data.
- **Visual Flow:** Experiment with the drag-and-drop pipeline builder.

## Notes

- PDF ingestion is not yet implemented.
- Embedding models are managed per collection.
- Data removal is supported by source.

## License

MIT License

---

*This project is for educational and prototyping purposes. Contributions welcome!*
