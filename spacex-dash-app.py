print("--- Running the latest debug code (FINAL ATTEMPT) ---") # Added for explicit version check

import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# --- Data Loading Section ---
# Load the dataset. This block includes more robust checks and feedback.
try:
    # Attempt to load from a local file first
    # This is the expected file name from the previous lab's output
    spacex_df = pd.read_csv("dataset_part_2.csv")
    print("Successfully loaded dataset_part_2.csv locally.")
except FileNotFoundError:
    print("dataset_part_2.csv not found locally. Attempting to download from URL.")
    try:
        # If not found locally, download from the course data URL
        spacex_df = pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/dataset_part_2.csv")
        print("Successfully downloaded and loaded dataset from URL.")
    except Exception as e:
        print(f"Error loading dataset from URL: {e}")
        spacex_df = pd.DataFrame() # Create an empty DataFrame if loading fails

# Check if DataFrame is empty after loading attempts
if spacex_df.empty:
    print("ERROR: DataFrame is empty. Please ensure 'dataset_part_2.csv' exists or the URL is accessible.")
else:
    print(f"DataFrame loaded successfully with {spacex_df.shape[0]} rows and {spacex_df.shape[1]} columns.")
    print("First 5 rows of the DataFrame:")
    print(spacex_df.head())

# Rename 'class' column to 'Class' for consistency with previous lab's output
# Some datasets might use 'class' as column name, while Plotly Express expects 'Class' (or we standardize it).
if 'class' in spacex_df.columns:
    spacex_df.rename(columns={'class': 'Class'}, inplace=True)
    print("Column 'class' renamed to 'Class'.")
if 'Class' not in spacex_df.columns:
    print("WARNING: 'Class' column (or 'class') not found in DataFrame. Plotting might fail.")


# --- Dash App Initialization ---
app = dash.Dash(__name__)

# Create a list of unique launch sites for the dropdown
# Ensure 'LaunchSite' column exists before trying to get unique values
if 'LaunchSite' in spacex_df.columns:
    launch_sites = spacex_df['LaunchSite'].unique().tolist()
    launch_sites.insert(0, 'All Sites') # Add an 'All Sites' option for filtering
else:
    print("WARNING: 'LaunchSite' column not found in DataFrame. Dropdown will be limited.")
    launch_sites = ['All Sites'] # Fallback if LaunchSite column is missing

# --- App Layout Definition ---
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Success Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),

    # Dropdown for Launch Site selection
    html.Div([
        html.Label("Select Launch Site:"),
        dcc.Dropdown(
            id='site-dropdown',
            options=[{'label': i, 'value': i} for i in launch_sites],
            value='All Sites',  # Default value for the dropdown
            placeholder="Select a Launch Site",
            searchable=True,
            style={'width': '100%'} # Style to make dropdown visible and responsive
        )
    ], style={'width': '80%', 'padding': '20px', 'margin': 'auto'}), # Center the dropdown

    # Scatter plot for Payload Mass vs. Flight Number
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),

    # Add a section for error messages/debug output in the UI
    html.Div(id='debug-output', style={'color': 'red', 'textAlign': 'center', 'padding': '10px'})
])

# --- Callback Function to update the plot ---
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    Output(component_id='debug-output', component_property='children'), # Output for debug messages in UI
    Input(component_id='site-dropdown', component_property='value')
)
def update_graph(selected_site):
    debug_message = "" # Initialize debug message

    # Handle case where DataFrame might be empty due to loading errors
    if spacex_df.empty:
        debug_message = "Error: No data loaded. Cannot generate plot."
        # Return an empty scatter plot with an informative title
        fig = px.scatter(title="Error: No data available to plot")
        return fig, debug_message

    # Filter data based on dropdown selection
    if selected_site == 'All Sites':
        filtered_df = spacex_df
        title = 'Payload Mass vs. Flight Number for All Launch Sites'
    else:
        filtered_df = spacex_df[spacex_df['LaunchSite'] == selected_site]
        title = f'Payload Mass vs. Flight Number for {selected_site}'

    # Handle case where filtering results in an empty DataFrame
    if filtered_df.empty:
        debug_message = f"No data found for {selected_site}. Please check your dataset or selection."
        fig = px.scatter(title=f"No Data for {selected_site}")
        return fig, debug_message

    # Check for required columns before plotting
    required_cols = ['FlightNumber', 'PayloadMass', 'Class', 'BoosterVersion', 'Outcome', 'LaunchSite', 'Orbit']
    if not all(col in filtered_df.columns for col in required_cols):
        missing_cols = [col for col in required_cols if col not in filtered_df.columns]
        debug_message = f"Missing one or more required columns for plotting: {', '.join(missing_cols)}. Check DataFrame structure."
        print(f"DEBUG: Missing columns: {missing_cols}") # Print to terminal as well
        fig = px.scatter(title="Error: Missing Data Columns for Plotting")
        return fig, debug_message

    # Create the scatter plot using Plotly Express
    fig = px.scatter(
        filtered_df,
        x='FlightNumber',
        y='PayloadMass',
        color='Class', # Color points based on success (1) or failure (0)
        hover_data=['BoosterVersion', 'Outcome', 'LaunchSite', 'Orbit'], # Display extra info on hover
        title=title,
        color_continuous_scale=px.colors.sequential.Viridis # Optional: adds a nice color scale
    )

    # Customize plot layout for aesthetics and readability
    fig.update_layout(
        xaxis_title="Flight Number",
        yaxis_title="Payload Mass (kg)",
        font=dict(size=12, color="#7f7f7f"), # General font styling
        margin=dict(l=50, r=50, t=80, b=50), # Adjust margins
        paper_bgcolor='white', # Background of the plot area
        plot_bgcolor='lightgrey' # Background of the plotting frame
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')

    return fig, debug_message

# --- Run the Dash Application ---
if __name__ == '__main__':
    # Running in debug mode provides useful error messages in the browser
    # Port 8050 is a common choice for Dash apps
    # Changed app.run_server() to app.run() due to ObsoleteAttributeException
    app.run(debug=True, port=8050)
