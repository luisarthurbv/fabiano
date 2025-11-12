# Fabiano Project

This project uses Python and Playwright for web automation.

## Project Setup

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <repository-url>
    cd fabiano
    ```

2.  **Install Python dependencies using Poetry:**
    If you don't have Poetry installed, follow the instructions on their official website: [https://python-poetry.org/](https://python-poetry.org/)

    Once Poetry is installed, run the following command in the project root to install dependencies:
    ```bash
    poetry install
    ```

3.  **Install Playwright browsers:**
    Playwright requires browser binaries to run. Install them using the following commands:
    ```bash
    poetry run playwright install
    ```

## Running the Project

To run the main script of the project, use:
```bash
poetry run python main.py
```
