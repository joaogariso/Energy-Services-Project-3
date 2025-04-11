import dash
from dash import html, dcc, Dash
from dash.dependencies import Input, Output
import dash_leaflet as dl
import pandas as pd

# Sample data

df = pd.read_csv("assets/detected_panels_clean.csv")


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

markers = [
    dl.CircleMarker(
        center=[row['latitude'], row['longitude']],
        color='blue' if row['type'] == 'PV' else 'red',
        radius=5,  # Adjust the size of the circle marker
        fill=True,
        fillOpacity=0.7,
        children=[
            dl.Tooltip(f"{row['id']} - {row['type']}"),
            dl.Popup(
                html.Div([
                    html.Img(
                        src=row['image_path'],
                        style={
                            'width': '300px', 
                            'height': 'auto', 
                            'marginBottom': '5px'}
                    ),
                    html.A(
                        "Open full image",
                        href=row['image_path'],
                        target="_blank",
                        style={
                            'display': 'block',
                             'color': 'green', 
                             'textDecoration': 'underline', 
                             'fontSize': '16px'},
                    )
                ], style={
                    'maxWidth': '500px', 
                    'overflow': 'hidden', 
                    'textAlign' : 'center'})
            )
        ]
    ) for index, row in df.iterrows()
]


# Dropdown for filtering
dropdown = dcc.Dropdown(
    id='type-filter',
    options=[
        {'label': 'ST & PV', 'value': 'both'},
        {'label': 'PV', 'value': 'PV'},
        {'label': 'ST', 'value': 'ST'}
    ],
    value='both',
    clearable=False,
    style={'width': '200px', 'margin': '10px'}
)


# Satellite layer
satellite_layer = dl.TileLayer(
    # url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    url='https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png',
    # url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
    attribution='Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
)

# Define the map
app.layout = html.Div([
    html.H1('Energy Services Project 3'),
    html.H3('João Gariso - 96400'),

    dcc.Tabs(id='tabs', value='project_introduction', children=[

        dcc.Tab(label='Project Introduction', value='project_introduction', children=[
            html.Div([
                html.H3('Overview'),
                html.P('This dashboard provides a comprehensive overview of my project focused on the identification and mapping of photovoltaic (PV) and solar thermal (ST) panels using images sourced from the Google Maps API, centered around Lisbon.'),

                html.H3('Data Collection'),
                html.Ul([
                    html.Li('Image Sourcing: Random snapshots were taken from the Google Maps API, focusing on urban and suburban areas across Portugal. A total of 375 images were curated, encompassing a diverse range of urban landscapes.'),
                    html.Li('Image Annotation: Using Roboflow, each image was manually examined to identify and annotate relevant features: 110 images contained no relevant features (null), 165 images featured photovoltaic (PV) panels, and 59 images displayed solar thermal (ST) panels. Annotations included 457 PV and 102 ST instances across the dataset.'),
                    html.Li('Enhanced Annotation for Misclassifications: Initial model outputs indicated frequent misclassifications of windows as panels. To mitigate this, 338 windows were annotated as a separate class to refine the training process and improve model accuracy.')
                ]),

                html.H3('Script Development'),
                html.P('A specialized script was developed to automate the image downloading process:'),
                html.Ul([
                    html.Li('Area Coverage: Images are downloaded covering a 3x3 km square area, with the center positioned on the Instituto Superior Técnico (IST).'),
                    html.Li('Overlap and Coordination: The script ensures some overlap between images for comprehensive coverage and stores the coordinates of each image’s central point in a CSV file for further processing.')
                ]),

                html.H3('Identification and Mapping'),
                html.P('Model Execution: Upon running the identification script, detections of PV or ST panels trigger a coordinate calculation for each panel based on its position within the image.'),
                html.P('Coordinate Conversion: To accurately map each panel, conversions are performed using the central coordinate. This involves calculating the offset from the center to the panel\'s location within the image.'),

                html.H3('Results Visualization'),
                html.P('The results of the PV and ST panel detections are dynamically displayed on the "Results" tab of this dashboard. This section visualizes the geographic distribution of identified panels, offering insights into the density and distribution of renewable energy installations across the surveyed areas.'),

                 html.H3('Results Discussion'),
                html.P('While the project has yielded important insights, the results are not without their imperfections. There are numerous instances of misidentifications, largely attributable to the suboptimal quality of the images used and the inherent challenge of distinguishing similar rectangular shapes such as windows and panels. Additionally, the dataset could benefit from expansion to improve the model’s learning and predictive accuracy, thereby enhancing overall performance.')
                
            ])
        ]),

        dcc.Tab(label='Results', value='results', children=[
            html.Div([
                dropdown,
                dl.Map(
                    [satellite_layer, dl.LayerGroup(id="marker-layer")],
                    center=[38.736763, -9.138933],  # Adjusted center between the two points
                    zoom=15,
                    style={'width': '100%', 'height': '800px'}
                )
            ])
        ])
    ])

    
])


# Callback to update map markers based on filter
@app.callback(
    Output('marker-layer', 'children'),
    Input('type-filter', 'value')
)
def update_markers(filter_type):
    if filter_type == 'both':
        filtered_df = df
    else:
        filtered_df = df[df['type'] == filter_type]

    markers = [
        dl.CircleMarker(
            center=[row['latitude'], row['longitude']],
            color='blue' if row['type'] == 'PV' else 'red',
            radius=5,
            fill=True,
            fillOpacity=0.7,
            children=[
                dl.Tooltip(f"{row['id']} - {row['type']}"),
                dl.Popup(
                    html.Div([
                        html.Img(src=row['image_path'], style={
                            'width': '300px',
                            'height': 'auto',
                            'marginBottom': '5px'
                        }),
                        html.A("Open full image", href=row['image_path'], target="_blank",
                               style={'display': 'block', 'color': 'green',
                                      'textDecoration': 'underline', 'fontSize': '16px'})
                    ], style={'maxWidth': '500px', 'overflow': 'hidden', 'textAlign': 'center'})
                )
            ]
        ) for _, row in filtered_df.iterrows()
    ]

    return markers

if __name__ == '__main__':
    app.run(debug=False)

