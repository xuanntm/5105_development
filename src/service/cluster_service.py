from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from src.model.esg_models import db, BEsgClusterAnalyisActual

def run_clustering(df):
    """
    Performs PCA and KMeans clustering on ESG data and saves results to DB.

    Parameters:
    - df: DataFrame with ESG scores
    - output_path: Path to save clustered DB
    - show_plot: Whether to display the PCA scatter plot

    Returns:
    - df: DataFrame with PCA and cluster labels
    """
    try:
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

        return df
    except Exception as e:
        print(str(e))
        print(f'run_clustering fail')
