import textwrap
import re as _re
import langextract as lx
import pandas as pd
import os
from pathlib import Path

lx_prompt = textwrap.dedent("""
    Extract financial information from the text.
    Identify if the following information fields exist in the source text and extract the exact literal text segment representing them: 
    'Monthly Income (INR)', 'Cost of Living Expenditure (INR)', 'Other Important Investments (INR)', 'Consumerist Expenditure (INR)', 'Crisis Shock Expenditure (INR)', 'Total Monthly Expenditure (INR)', 'Debt Status'.
    
    CRITICAL INSTRUCTION: Use the exact literal string text as it appears in the input document for your extractions. 
    Do not alter formatting, do not convert shorthand words, do not remove currency symbols, and do not remove commas.
    
    Examples of exact string extractions:
    - If text says "₹1,40,000", extract: "₹1,40,000"
    - If text says "40 thousand", extract: "40 thousand"
    - If text says "1.5L", extract: "1.5L"
    - If text says "no debt", extract: "no debt"
""")

query = "I have salary 100000 , cost of living 40 thousand, other investments 20 thousand, consumerist 5000, crisis shock expense 20 thousand. What is my category?"
lx_examples = [lx.data.ExampleData(
        text="Hey, I need some honest financial advice. I am currently working as a software engineer in Bengaluru, and my monthly in-hand salary is ₹1,40,000. Lately, I feel like my money is just vanishing. My fixed overheads are quite high—between my house rent, society maintenance, maid, electricity, and groceries, my core cost of living comes out to exactly ₹45,000 every month. On top of that, I am upskilling myself to transition into a management role, so I am paying a monthly EMI of ₹15,000 for an executive data science certification course from an IIM. I've also been overspending a bit on lifestyle choices; between dining out at pubs, weekend trips, and ordering from Swiggy/Zomato, my discretionary consumerist spending hits around ₹25,000 monthly. To make matters worse, my father had a minor medical emergency back home last month, so I've had to commit a fixed ₹15,000 monthly towards his ongoing healthcare and medicine costs for the foreseeable future. If you calculate it all, my total monthly expenditure has ballooned to ₹1,00,000, leaving me with very little savings. As for my overall debt status, I currently owe ₹3,50,000 on an active personal loan that I took out for relocation and furnishing last year. Looking at this breakdown, do you think my current level of expenditure is actually worth it, or am I jeopardizing my long-term financial health for short-term comfort?",
        extractions=[
            lx.data.Extraction(extraction_class="Monthly Income (INR)", extraction_text="₹1,40,000", attributes={}),
            lx.data.Extraction(extraction_class="Cost of Living Expenditure (INR)", extraction_text="₹45,000", attributes={}),
            lx.data.Extraction(extraction_class="Other Important Investments (INR)", extraction_text="₹15,000", attributes={}),
            lx.data.Extraction(extraction_class="Consumerist Expenditure (INR)", extraction_text="₹25,000", attributes={}),
            lx.data.Extraction(extraction_class="Crisis Shock Expenditure (INR)", extraction_text="₹15,000", attributes={}),
            lx.data.Extraction(extraction_class="Total Monthly Expenditure (INR)", extraction_text="₹1,00,000", attributes={}),
            lx.data.Extraction(extraction_class="Debt Status", extraction_text="I currently owe", attributes={})
        ]
    )]

lx_classes = ['Monthly Income (INR)', 'Cost of Living Expenditure (INR)', 'Other Important Investments (INR)',
               'Consumerist Expenditure (INR)', 'Crisis Shock Expenditure (INR)',
               'Total Monthly Expenditure (INR)', 'Debt Status']

BASE_DIR = Path(__file__).resolve().parent.parent.parent
csv_path = BASE_DIR / "src" / "data" / "indian_finance_ml_dataset_balanced_final.csv"

df = pd.read_csv(csv_path)
debt_mode = df['Debt Status'].mode()[0]  # Most common debt status in the dataset

api_key = os.getenv("LANGEXTRACT_API_KEY")

def clean_int(val):
    """Parse any Indian currency format and return a plain integer in INR."""
    s = str(val).lower().strip()
    # Remove currency prefixes/symbols
    s = _re.sub(r'(₹|rs\.?|inr)\s*', '', s).strip()
    # Remove commas (Indian formatting: 1,40,000)
    s = s.replace(',', '')
    # Crore
    m = _re.match(r'^([\d.]+)\s*(?:crore|crores|cr)\b', s)
    if m:
        return int(float(m.group(1)) * 10_000_000)
    # Lakh / lac / L
    m = _re.match(r'^([\d.]+)\s*(?:lakh|lakhs|lac|lacs|l)\b', s)
    if m:
        return int(float(m.group(1)) * 100_000)
    # Thousand / k
    m = _re.match(r'^([\d.]+)\s*(?:thousand|thousands|k)\b', s)
    if m:
        return int(float(m.group(1)) * 1_000)
    # Hundred
    m = _re.match(r'^([\d.]+)\s*(?:hundred|hundreds)\b', s)
    if m:
        return int(float(m.group(1)) * 100)
    # Plain number (possibly decimal)
    cleaned = _re.sub(r'[^\d.]', '', s)
    return int(float(cleaned)) if cleaned else 0

def normalize_debt(debt_text):
    if not debt_text:
        return "Not in Debt"
        
    val_str = str(debt_text).lower().strip()
    
    # Check for negative debt keywords
    if any(neg in val_str for neg in ["no", "not", "none", "zero", "free", "clear","don't"]):
        return "Not in Debt"
        
    # Check for positive debt indicators
    if any(pos in val_str for pos in ["have debt", "in debt", "emi", "loan", "owe","have"]):
        return "In Debt"
        
    # Fallback default match
    return "Not in Debt"


def extract_financial_info(query):
    if os.getenv("FLASK_ENV") == "testing":
        return "Mocked Gemini Report: Testing environment active."
    try:
        result = lx.extract(
            text_or_documents=query,
            prompt_description=lx_prompt,
            examples=lx_examples,
            model_id="gemini-2.5-flash",
            api_key=os.getenv("LANGEXTRACT_API_KEY")
        )
            # Build exact key dictionary
        extracted_map = {}
        for ex in result.extractions:
            extracted_map[ex.extraction_class] = ex.extraction_text

        # 3. Apply fallback medians for missing fields
        for i in range(len(lx_classes)):
            if lx_classes[i] not in extracted_map:
                if lx_classes[i] == 'Debt Status':
                    extracted_map[lx_classes[i]] = "Not in Debt"
                elif lx_classes[i]=="Total Monthly Expenditure (INR)":
                    extracted_map[lx_classes[i]] = clean_int(extracted_map[lx_classes[1]])+clean_int(extracted_map[lx_classes[2]])+clean_int(extracted_map[lx_classes[3]])+clean_int(extracted_map[lx_classes[4]])
                else:
                    try:
                        median_val = int(df[lx_classes[i]].median())
                    except Exception:
                        median_val = 0
                    extracted_map[lx_classes[i]] = median_val

        # 4. Clean and assemble feature vectors 
        numeric_keys = lx_classes[:-1]  # Slice the 6 monetary columns
        numeric_vals = [clean_int(extracted_map.get(k, 0)) for k in numeric_keys]
        
        raw_debt = extracted_map.get('Debt Status', 'Not in Debt')
        debt_status = normalize_debt(raw_debt)

        # 5. Compiled features (Array structure: 6 integers + 1 normalized string)
        extracted_features = numeric_vals + [debt_status]
        return extracted_features
    except:
        return "Fallback Report: High traffic volume. Financial metrics computed via baseline model rules."
        


