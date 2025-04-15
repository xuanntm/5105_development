import pandas as pd
from src.config.confidence_config import confidence_model
from sentence_transformers import SentenceTransformer, util
from src.model.esg_models import db, EsgExtractedMetricData

# Load the SentenceTransformer model
confidence_model = SentenceTransformer('all-MiniLM-L6-v2')

# Metric Dictionary of known aliases
metric_dictionary = {
    "GHG emissions - Total Emission": [
        "Total GHG emissions", "Overall greenhouse gas emissions", "Total emissions (GHG)", "GHG total output",
        "Total GHGs", "Total Emission GHG Emissions (tCO2e / $ revenue)",
        "Renewable Energy Ratio GHG Emissions (Onsite Solar Share in Total Energy Consumption)","Total operational GHG emissions"
    ],
    "GHG emissions - Scope 1": [
        "Scope 1 GHG emissions", "Direct GHG emissions", "Emissions from owned sources", "Scope 1 emissions",
        "Scope 1 GHG Emissions (Metric Tons CO2eq)", "Scope 1 GHG Emissions (operational control):",
        "direct GHG emissions (scope 1)","Scope 1 Emissions (Operational Boundary)"
    ],
    "GHG emissions - Scope 2": [
        "Scope 2 GHG emissions", "Indirect GHG emissions from energy", "Purchased electricity emissions",
        "Scope 2 GHG Emissions (market-based method)", "Scope 2 GHG Emissions (Metric Tons CO2eq (market-based))",
        "indirect GHG emissions (scope 2), market-based","Scope 2 Emissions (Operational Boundary)"
    ],
    "GHG emissions - Scope 3": [
        "Scope 3 GHG emissions", "Value chain emissions", "Indirect emissions (Scope 3)",
        "Scope 3 GHG Emissions (Metric Tons CO2eq)","Scope 3 emissions (use of sold products)"
    ],
    "GHG emissions - Scope 1, 2, 3": [
        "Total GHG emissions (Scopes 1+2+3)", "Combined scope emissions", "GHG Scope 1 2 3",
        "Scope 1, 2, and 3 emissions total"
    ],
    "GHG Intensity - Total Emission": [
        "GHG intensity (total)", "Emissions per unit output", "Total GHG intensity", "Carbon intensity"
    ],
    "GHG Intensity - Production of Energy": [
        "GHG per energy produced", "Emission intensity per energy", "Carbon intensity of energy", "GHG/Energy unit"
    ],
    "Land Use - Land Restored and or Rehabilitated": [
        "Land restored", "Land rehabilitation", "Reclaimed land", "Restored ecosystems"
    ],
    "Aggregate Volume of Hydrocarbon spills and leaks": [
        "Total hydrocarbon spills", "Oil spill volume", "Hydrocarbon leak incidents", "Volume of leaked hydrocarbons","Volume of oil spilled"
    ],
    "Water Consumption": [
        "Water usage", "Total water consumed", "Freshwater withdrawal", "Water intake", "Freshwater consumption"
    ],
    "Water Waste": [
        "Wastewater", "Water discharge", "Used water", "Water effluent", "Discharges to water – Refining and chemicals total water discharged"
    ],
    "Electronic Waste": [
        "E-waste", "Disposed electronics", "Electronic disposal", "IT waste"
    ],
    "Packaging Material Waste": [
        "Packaging waste", "Material used in packaging", "Waste from packaging", "Packaging material disposal"
    ],
    "Air Pollutant Emission - Nox": [
        "NOx emissions", "Nitrogen oxide emissions", "Air pollutants - NOx", "Emissions of NOx", "Air emissions – nitrogen oxides"
    ],
    "Air Pollutant Emission - Sox": [
        "SOx emissions", "Sulfur oxide emissions", "Air pollutants - SOx", "Emissions of SOx", "Air emissions – sulfur oxides"
    ],
    "Air Pollutant Emission - VOC": [
        "VOC emissions", "Volatile Organic Compounds emissions", "Air pollutants - VOC", "Emissions of VOCs", "Air emissions – non-methane hydrocarbons"
    ],
    "Air Pollutant Emission - PM10": [
        "PM10 emissions", "Particulate matter (PM10)", "Air pollutants - PM10", "Fine particle emissions","Air Pollutant Emission - PM10"
    ],
    "Air Pollutant Emission - Total": [
        "Total air pollutant emissions", "Combined air emissions", "Aggregate air pollutants", "All air emissions", "Total emissions to air", "Air Pollutant Emission - Total"
    ],
    "Toxic Waste": [
        "Hazardous waste", "Toxic chemical waste", "Dangerous waste", "Industrial toxic waste",
        "Amount of hazardous waste manifested for disposal"
    ],
    "Renewable Energy Ratio": [
        "Renewables share", "Proportion of renewable energy", "Renewable energy usage", "Green energy ratio","Renewable Energy Ratio"
    ],
    "Human Rights Policies": [
        "Human rights policy", "Policy on human rights", "Human rights commitment", "HR policy framework",
        "A formal Human Rights Policy exists, aligned with international standards","Human Rights Policies"
    ],
    "Third Party Audits on Labour Sites": [
        "Labor site audits", "Third-party labor inspections", "Worker rights audits", "External labor assessments","Third Party Audits on Labour Sites"
    ],
    "Total Recordable Incident Rate (TRIR)": [
        "TRIR", "Workplace incident rate", "Recordable injury rate", "Occupational incident rate", "Recordable injury frequency (RIF) – workforce"
    ],
    "Fatality Rate": [
        "Workplace fatality rate", "Employee death rate", "Fatal incidents", "Fatal accidents","Fatalities – workforce"
    ],
    "Average Training Hours per Employees": [
        "Training hours per employee", "Employee training average", "Avg. hours of training",
        "Training time per staff", "Average number of training hours per employee in 2023"
    ],
    "Presence/Absence of grievance mechanisms": [
        "Grievance mechanism in place", "Complaint system", "Employee grievance channels",
        "Whistleblower or feedback system"
    ],
    "Percentage of Women on Board": [
        "Women board representation", "Female directors", "Gender diversity in board", "Women in boardroom","percentage female – board of directors"
    ],
    "Percentage of Independent VS Non-Independent Directors": [
        "Independent director ratio", "Board independence", "Proportion of non-independent directors",
        "Independent vs affiliated board"
    ],
    "Pay of Senior execs linked to sustainability KPI achievement": [
        "Executive pay tied to ESG", "Sustainability-linked compensation", "ESG performance-based bonus",
        "KPI-linked executive salary"
    ],
    "Accounting Disclosure": [
        "Financial reporting", "Transparency in accounting", "Disclosure of financials", "Audit and accounting details"
    ],
    "coverage of business ethics policies, presence of audits on policies": [
        "Business ethics policy coverage", "Audits of ethics policies", "Corporate ethics framework",
        "Integrity policy reviews"
    ],
    "presence/absence of a clear tax strategy, policy, and governance framework": [
        "Tax governance policy", "Tax strategy disclosure", "Corporate tax transparency", "Tax compliance framework"
    ],
    "Shareholder Voting Rights": [
        "Voting rights for shareholders", "Equity holder voting power", "Shareholder democracy",
        "Investor voting structure"
    ]
}

def calculate_confidence_scores(company_name, report_year):
    try:
        data = db.session.query(EsgExtractedMetricData).with_entities(
            EsgExtractedMetricData.pillar,
            EsgExtractedMetricData.metric,
            EsgExtractedMetricData.extracted_metric,
            EsgExtractedMetricData.extracted_value
        ).filter_by(company_name=company_name, year=report_year).all()

        metrics = [{
            'Metric': row.metric, 
            'Extracted Metric': row.extracted_metric, 
            'extracted_value': row.extracted_value
        }for row in data]
        
        df = pd.DataFrame(metrics)
        print(df)

        results = []
        for idx, row in df.iterrows():
            metric = str(row.get('Metric', '')).strip()
            extracted = str(row.get('Extracted Metric', '')).strip()
            if metric and extracted:
                base_embedding = confidence_model.encode(extracted.lower(), convert_to_tensor=True)

                aliases = metric_dictionary.get(metric, [metric])
                best_score = -1
                best_alias = None

                for alias in aliases:
                    alias_embedding = confidence_model.encode(alias.lower(), convert_to_tensor=True)
                    score = float(util.cos_sim(base_embedding, alias_embedding).item())
                    if score > best_score:
                        best_score = score
                        best_alias = alias

                results.append({
                    "Metric": metric,
                    "Best_Matching_Alias": best_alias,
                    "Extracted_Metric": extracted,
                    "Confidence_Score": round(best_score, 3),
                    "Needs_Human_Review": best_score < 0.75
                })

        confidence_df = pd.DataFrame(results)
        # print(confidence_df)
        mean_score = confidence_df["Confidence_Score"].mean()
        print(f"\n📈 Mean Confidence Score: {round(mean_score, 3)}")
        return df
    except Exception as e:
        print(f'calculate_confidence_scores fail for {company_name} {report_year}')

