from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from src.model.esg_models import db, BEsgClusterAnalyisActual

def run_clustering(df):
    """
    Performs PCA and KMeans clustering on ESG data and saves results to CSV.

    Parameters:
    - df: DataFrame with ESG scores
    - output_path: Path to save clustered CSV
    - show_plot: Whether to display the PCA scatter plot

    Returns:
    - df: DataFrame with PCA and cluster labels
    """
    scaler = StandardScaler()
    esg_features = df[['Environmental Score', 'Social Score', 'Governance Score', 'ESG Score']]
    scaled_esg = scaler.fit_transform(esg_features)

    # PCA
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(scaled_esg)
    df['PCA1'], df['PCA2'] = pca_result[:, 0], pca_result[:, 1]

    # KMeans
    kmeans = KMeans(n_clusters=3, random_state=42)
    df['Cluster'] = kmeans.fit_predict(scaled_esg)
    df=df[['Year','Company_name','Environmental Score','Social Score','Governance Score','ESG Score','PCA1','PCA2','Cluster']]
    
    # Save output
    # df.to_csv(output_path, index=False)

    BEsgClusterAnalyisActual
    def process_row(row):
        return BEsgClusterAnalyisActual(
            Year=row['Year'],
            company_name=row['Company_name'],
            Environmental_Score=row['Environmental Score'],
            Social_Score=row['Social Score'],
            Governance_Score=row['Governance Score'],
            ESG_Score=row['ESG Score'],
            PCA1=row['PCA1'],
            PCA2=row['PCA2'],
            Cluster=row['Cluster'],
            data_type='DEMO'
        )
    # Apply the function to each row
    results = df.apply(process_row, axis=1)
    db.session.add_all(results)
    db.session.commit()

    # inserted_records = [
    #     {
    #         'id': record.id,
    #         'Company_name': record.company_name,
    #         'Year': record.Year,
    #         'Environmental_Score': record.Environmental_Score,
    #         'Social_Score': record.Social_Score,
    #         'Governance_Score': record.Governance_Score,
    #         'ESG_Score': record.ESG_Score,
    #         'ESG_Rating': record.ESG_Rating,
    #         'ESG_Rank': record.ESG_Rank,
    #         'data_type': record.data_type,
    #         'created_date': record.created_date.isoformat()  # Format the datetime
    #     } for record in results
    # ]

    # Print cluster summary
    # clustered_companies = df[["Company_name", "Cluster"]]
    # print(clustered_companies.to_string(index=False))

    return df