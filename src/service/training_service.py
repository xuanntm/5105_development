from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
from src.model.esg_models import ReportHistory



def load_esg_model(company_name, report_year):
    """
    Fine-tunes a SentenceTransformer model using ESG-related sentence pairs
    extracted from a company's uploaded sustainability report.

    The function:
    1. Retrieves the most recent report for the specified company and year.
    2. Simulates sentence pair training data from the report's text (synthetic similarity of 0.8).
    3. Fine-tunes a pre-trained model using cosine similarity loss.
    4. Saves the adapted model for ESG-specific applications (e.g., greenwashing detection).

    Parameters:
    company_name (str): The name of the company to load the report from.
    report_year (int): The report year to locate the document.

    Returns:
    None

    Exceptions:
    Prints the error message if any part of the pipeline fails.
    """
    try:
        # Step 1: Load the energy-sector ESG data
        # with open(f'{DATA_FOLDER_JSON}{company_name}{report_year}.json', 'r') as f:
        #     data = json.load(f)
        data = ReportHistory.query.filter_by(company_name=company_name, year=report_year) \
            .order_by(ReportHistory.created_date.desc()).first()


        # Step 2: Extract and prepare ESG-related sentence pairs (for example purposes)
        # We'll simulate sentence pairs and similarity scores
        pages = data.get("pages", [])
        examples = []

        # Use nearby sentences or duplicates with synthetic similarity scores
        for i in range(0, len(pages)-1, 2):
            sent1 = pages[i].strip()
            sent2 = pages[i+1].strip()
            # Assume sentences on nearby pages are somewhat similar (label between 0.5 and 1.0)
            examples.append(InputExample(texts=[sent1, sent2], label=0.8))

        # Step 3: Load a pre-trained SentenceTransformer model
        model = SentenceTransformer('all-MiniLM-L6-v2')

        # Step 4: Prepare data loader
        train_dataloader = DataLoader(examples, shuffle=True, batch_size=8)

        # Step 5: Define cosine similarity loss
        train_loss = losses.CosineSimilarityLoss(model)

        # Step 6: Fine-tune the model
        model.fit(
            train_objectives=[(train_dataloader, train_loss)],
            epochs=10,
            warmup_steps=10,
            show_progress_bar=True
        )

        # Step 7: Save the adapted ESG-energy-sector model
        model.save("energy_esg_adapted_model")
        print("Model fine-tuned and saved!")
    except Exception as e:
        print(str(e))
        print(f'load_esg_model fail for {company_name} {report_year}')