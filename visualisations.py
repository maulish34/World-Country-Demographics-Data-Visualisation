import pandas as pd
import numpy as np
import altair as alt
from altair import datum
import geopandas as gpd
from vega_datasets import data
from ipywidgets import widgets
from IPython.display import display
import textwrap

# Load the dataset
df = pd.read_csv('world-data-2023_cleaned.csv')

# Define color scale for continents
continent_color_scale = alt.Scale(
    domain=['Asia', 'Europe', 'Africa', 'Americas', 'Oceania'],
    range=['#7570b3', '#66a61e', '#fdc086', '#e7298a', '#d95f02']
)

# Define selections
country_selection = alt.selection_point(
    fields=['country-code'],
    empty=False,
)

hover = alt.selection_point(on='pointerover', empty=False, nearest=True)

continent_selection = alt.selection_point(
    fields=['region'],
)

brush_selection = alt.selection_interval(
    mark=alt.BrushConfig(cursor='zoom-in', fill='#737070', fillOpacity=0.2, stroke='black', strokeWidth=1),
)

# Legend for continents
legend = alt.Chart(df).transform_aggregate(
    groupby=['region']
).mark_point().encode(
    y=alt.Y('region:N', axis=alt.Axis(title=None, labelAngle=-90)),
    color=alt.Color('region:N', scale=continent_color_scale, legend=None),
    opacity=alt.condition(continent_selection & brush_selection, alt.value(1), alt.value(0.2)),
    fill=alt.Color('region:N', scale=continent_color_scale, legend=None),
    fillOpacity=alt.condition(continent_selection & brush_selection, alt.value(0.8), alt.value(0.2)),
    size=alt.condition(hover, alt.value(300), alt.value(150)),
).add_params(
    continent_selection, brush_selection, hover
).properties(
    title='Continent'
)

# Base map layers
sphere = alt.sphere()
graticule = alt.graticule()
basemap = (
    alt.layer(
        alt.Chart(sphere).mark_geoshape(fill='#c9e3ff'),
        alt.Chart(graticule).mark_geoshape(stroke='gray', strokeWidth=0.5),
    )
)

# Load and merge map data
url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
country_shapes = gpd.read_file(url)
country_shapes = country_shapes[['NAME', 'ISO_A3', 'geometry']]
country_shapes['alpha-3'] = country_shapes['ISO_A3']

# adding missing or unmatched alpha-3 codes
country_shapes.loc[country_shapes['NAME'] == 'Norway', 'alpha-3'] = 'NOR'
country_shapes.loc[country_shapes['NAME'] == 'France', 'alpha-3'] = 'FRA'
country_shapes.loc[country_shapes['NAME'] == 'Kosovo', 'alpha-3'] = 'XKX'
country_shapes.loc[country_shapes['NAME'] == 'Somaliland', 'alpha-3'] = 'SOM'
country_shapes.loc[country_shapes['NAME'] == 'Taiwan', 'alpha-3'] = 'TWN'
country_shapes.loc[country_shapes['NAME'] == 'Montenegro', 'alpha-3'] = 'MNE'


print(country_shapes.columns)

map_data = pd.merge(country_shapes, df, on='alpha-3', how='left')

map_data['highlight'] = False
df['highlight'] = False

# Selection box for indicators
selection_columns = ['GDP per Capita', 'Life expectancy', 'CO2 Emissions per Capita', 'Unemployment rate']
selection_box = alt.binding_select(options=selection_columns, labels=['GDP per Capita (in USD)', 'Life expectancy (years)', 'CO2 Emissions per Capita (tonnes)', 'Unemployment rate (% of labour force)'], name='Select an Indicator to display on map: ')
selection = alt.selection_point(fields=['Indicator'], bind=selection_box, value='GDP per Capita')


# Choropleth map
choropleth_map = alt.Chart(map_data, 
    title=alt.Title("Choropleth map of Country demographics",
        subtitle="Set to GDP per Capita by default, choose a different indicator from the dropdown menu at the bottom of the page."
)).transform_fold(
    selection_columns,
    as_=['Indicator', 'Value']
).transform_filter(
    selection    
).mark_geoshape(
    stroke='white',
    strokeWidth=0.7
).encode(
    shape='geometry:G',
    color=alt.Color('Value:Q',
                   scale=alt.Scale(scheme='viridis'),
                   title='Selected Indicator'),
    opacity=alt.condition(
        continent_selection & country_selection & brush_selection,
        alt.value(1),
        alt.value(0.3)
    ),
    tooltip=[
        alt.Tooltip('Country:N', title='Country'),
        alt.Tooltip('GDP per Capita:Q', title='GDP per Capita (USD):'),
        alt.Tooltip('Life expectancy:Q', title='Life Expectancy (years):'),
        alt.Tooltip('CO2 Emissions per Capita:Q', title='CO₂ Emissions per Capita (tonnes):'),
        alt.Tooltip('Unemployment rate:Q', title='Unemployment Rate (% of labour force):')
    ]
).project(
    type='equalEarth'
).add_params(
    country_selection, selection
).properties(
    width=900,
    height=540,
    # title='GDP per Capita across the World' 
)

final_map = basemap + choropleth_map 

# Filter outliers for scatter plot
df_filtered = df[~df['Country'].isin(['Luxembourg', 'Liechtenstein', 'Monaco'])]

# Scatter plot for GDP vs Life Expectancy
gdp_life_expectancy_scatter = alt.Chart(
    df_filtered, 
    title=alt.Title("GDP per Capita vs Life Expectancy accros countries",
                subtitle="With Population as size of the points")
    ).mark_point().encode(
    x=alt.X('GDP per Capita:Q', title='GDP per Capita (in USD)'),
    y=alt.Y('Life expectancy:Q', title='Life Expectancy (years)', scale=alt.Scale(domain=[df_filtered['Life expectancy'].min() - 5, df_filtered['Life expectancy'].max() + 5])),
    color=alt.Color('region:N', scale=continent_color_scale, legend=None),
    opacity=alt.condition(country_selection & brush_selection, alt.value(1), alt.value(0.25)),
    fill=alt.Color('region:N', scale=continent_color_scale, legend=None),
    fillOpacity=alt.condition(country_selection & brush_selection, alt.value(0.6), alt.value(0.2)),
    size=alt.Size('Population:Q', legend=None, scale=alt.Scale(range=[70, 3000]), title='Population'),
    order=alt.condition(country_selection & continent_selection & brush_selection, alt.value(1), alt.value(0)),
    tooltip=[
        alt.Tooltip('Country:N', title='Country:'),
        alt.Tooltip('GDP per Capita:Q', title='GDP per Capita:'),
        alt.Tooltip('Life expectancy:Q', title='Life Expectancy:'),
        alt.Tooltip('Population:Q', title='Population:'),
        alt.Tooltip('region:N', title='Continent:')
    ]
).add_params(
    country_selection, brush_selection
).transform_filter(
    continent_selection
).properties(
    width=560,
    height=540
)

# Average CO2 emissions bar chart
continent_avg_co2 = df.groupby('region').agg({'CO2 Emissions per Capita': 'mean'}).reset_index()
average_co2_emissions_bar_chart = alt.Chart(continent_avg_co2).mark_bar().encode(
    y=alt.Y('region:N', axis=alt.Axis(title='Continent')),
    x=alt.X('CO2 Emissions per Capita:Q', axis=alt.Axis(title='Average CO₂ Emissions per Capita')),
    color=alt.value('grey'),
    opacity=alt.condition(continent_selection, alt.value(0.4), alt.value(0.1)),
    tooltip=[
        alt.Tooltip('region:N', title='Continent:'),
        alt.Tooltip('CO2 Emissions per Capita:Q', title='Average CO₂ Emissions per Capita:')
    ]
).properties(
    width=640,
    height=540
)

# Filter outliers for CO2 scatter plot
df_filtered = df[~df['Country'].isin(['Qatar', 'Trinidad and Tobago'])]

# Scatter plot for CO2 emissions
country_co2_scatter = alt.Chart(df_filtered).mark_point().encode(
    y=alt.Y('region:N', axis=alt.Axis(title='Continent')),
    x=alt.X('CO2 Emissions per Capita:Q', axis=alt.Axis(title='CO₂ Emissions per Capita (tonnes)')),
    color=alt.Color('region:N', scale=continent_color_scale, legend=None),
    fill=alt.Color('region:N', scale=continent_color_scale, legend=None),
    fillOpacity=alt.condition(country_selection & brush_selection, alt.value(0.6), alt.value(0.2)),
    opacity=alt.condition(country_selection & brush_selection, alt.value(1), alt.value(0.25)),
    order=alt.condition(country_selection & continent_selection & brush_selection, alt.value(1), alt.value(0)),
    size=alt.when(hover).then(alt.value(500)).otherwise(alt.value(100)),
    tooltip=[
        alt.Tooltip('Country:N', title='Country:'),
        alt.Tooltip('CO2 Emissions per Capita:Q', title='CO₂ Emissions per Capita:'),
        alt.Tooltip('region:N', title='Continent:')
    ]
).add_params(
    country_selection, brush_selection, hover
).transform_filter(
    continent_selection
)

# Combined emissions chart
emissions_chart = alt.layer(
    average_co2_emissions_bar_chart,
    country_co2_scatter,
    title=alt.Title("CO2 Emissions per Capita accross Countries and Continents")
).resolve_scale(
    y='shared'
).properties(
    width=640,
    height=540,
)

# Health indicators for parallel plot
health_indicators = [
    'Physicians per thousand',
    'Life expectancy',
    'Fertility Rate',
    'Infant mortality',
    'Maternal mortality ratio',
    'Out of pocket health expenditure'
]

# Drop rows with missing health indicators
df_health = df.dropna(subset=health_indicators)

# Parallel plot for health indicators
parallel_plot = alt.Chart(df_health,
    title=alt.Title("Parallel plot of Health demographics across countries",
                    subtitle="Values are scaled for relative comparison, hover over datapoints for actual values")
                                                
).transform_window(
    index='count()'
).transform_fold(
    health_indicators,
    as_=['Indicator', 'Value']
).transform_joinaggregate(
    min_value='min(Value)',
    max_value='max(Value)',
    groupby=['Indicator']
).transform_calculate(
    minmax_value='(datum.Value - datum.min_value) / (datum.max_value - datum.min_value)'
).mark_line().encode(
    x=alt.X('Indicator:N', title='Health Indicators', sort=health_indicators, axis=alt.Axis(labelAngle=-15)),
    y=alt.Y('minmax_value:Q', scale=alt.Scale(zero=False), title='Scaled value, between minimum and maximum for each indicator'),
    color=alt.Color('region:N', scale=continent_color_scale, legend=None),
    opacity=alt.condition(
        country_selection & brush_selection,
        alt.value(0.8),
        alt.value(0.05)
    ),
    order=alt.condition(
        country_selection & brush_selection,
        alt.value(1),
        alt.value(0)
    ),
    detail='alpha-3:N',
    tooltip=[
        alt.Tooltip('Country:N', title='Country:'),
        alt.Tooltip('Indicator:N'),
        alt.Tooltip('Value:Q')
    ]
).add_params(
    country_selection,
    # brush_selection
).transform_filter(
    continent_selection
).properties(
    width=900,
    height=540
)

# Education indicators
education_indicators = ['Gross primary education enrollment (%)', 'Gross tertiary education enrollment (%)']
df_education = df.dropna(subset=education_indicators)
continent_avg_education = df_education.groupby('region').agg({
    'Gross primary education enrollment (%)': 'mean',
    'Gross tertiary education enrollment (%)': 'mean'
}).reset_index()

# Melt education data for bar chart
education_data = continent_avg_education.melt(
    id_vars=['region'],
    value_vars=education_indicators,
    var_name='Education Level',
    value_name='Rate'
)

# Bar chart for education rates
education_bar = alt.Chart(education_data).mark_bar().encode(
    x=alt.X('Rate:Q', axis=alt.Axis(title='Gross education enrollment (%, tertiary and primary)')),
    y=alt.Y('region:N', sort='-x', axis=alt.Axis(title='Continent')),
    color=alt.Color('Rate:Q', legend=None),
    opacity=alt.condition(continent_selection, alt.value(0.4), alt.value(0.1)),
    tooltip=[
        alt.Tooltip('region:N', title='Continent:'),
        alt.Tooltip('Education Level:N', title='Education Level:'),
        alt.Tooltip('Rate:Q', title='Average Rate:')
    ]
)

# Unemployment scatter plot
df_unemployment = df.dropna(subset=['Unemployment rate'])

unemployment_scatter = alt.Chart(df_unemployment).mark_point(size=100).encode(
    y=alt.Y('region:N', axis=alt.Axis(title='Continent')),
    x=alt.X('Unemployment rate:Q', axis=alt.Axis(title='Unemployment Rate (% of labour force)')),
    color=alt.Color('region:N', scale=continent_color_scale, legend=None),
    fill=alt.Color('region:N', scale=continent_color_scale, legend=None),
    fillOpacity=alt.condition(country_selection & brush_selection, alt.value(0.6), alt.value(0.2)),
    opacity=alt.condition(country_selection & brush_selection, alt.value(1), alt.value(0.25)),
    order=alt.condition(country_selection & continent_selection & brush_selection, alt.value(1), alt.value(0)),
    size=alt.when(hover).then(alt.value(500)).otherwise(alt.value(100)),
    tooltip=[
        alt.Tooltip('Country:N', title='Country'),
        alt.Tooltip('Gross primary education enrollment (%):Q', title='Gross Primary Education Enrollment %:'),
        alt.Tooltip('Gross tertiary education enrollment (%):Q', title='Gross Tertiary Education Enrollment %:'),
        alt.Tooltip('Unemployment rate:Q', title='Unemployment Rate (%)'),
    ]
).add_params(
    country_selection, brush_selection, hover
).transform_filter(
    continent_selection
)

# Combined education and unemployment chart
education_unemployment_chart = alt.layer(
    education_bar,
    unemployment_scatter
).resolve_scale(
    x='independent'
).properties(
    width=640,
    height=540,
    title='Education enrollment and Unemployment accross Countries and Continents' 
)

# Country statistics table
indicators = ['Country', 'Population', 'GDP per Capita', 'Gross primary education enrollment (%)', 'Gross tertiary education enrollment (%)', \
                'Unemployment rate', 'CO2 Emissions per Capita', 'Life expectancy', 'Physicians per thousand', 'Fertility Rate', 'Infant mortality', \
                    'Maternal mortality ratio', 'Out of pocket health expenditure']



selected_data = alt.Chart(df, 
                          title=alt.Title("Country statistics",
                        subtitle=["Select only one", "country to view data"]
)).transform_filter(
    country_selection
).transform_fold(
    indicators,
    as_=['Indicator', 'Value']
).mark_text(align='left').encode(
    y=alt.Y('Indicator:N', sort=indicators, axis=alt.Axis(title=None, labelExpr='[slice(datum.label, 0, 20), slice(datum.label, 20)]')),
    text=alt.Text('Value:N')
).properties(
    width=120,
    height=540,
)



# Combine charts into dashboard
top_row = alt.hconcat(
    final_map.properties(width=670, height=395),
    selected_data.properties(width=120, height=395),
    parallel_plot.properties(width=710, height=395),
    # selected_data.properties(width=120, height=395)
).resolve_scale(
    color='independent'
)

bottom_row = alt.hconcat(
    legend.properties(width=80, height=250),
    education_unemployment_chart.properties(width=500, height=365),
    emissions_chart.properties(width=500, height=365),
    gdp_life_expectancy_scatter.properties(width=500, height=365)    
).resolve_scale(
    color='independent'
)

dashboard = alt.vconcat(
    top_row,
    bottom_row
).properties(
    title=alt.Title("Socio-Economic and Health Demographics Across Countries and Continents", 
                    subtitle=["Use interactive features to filter data by continents or to highlight countries for comparision and exploration.", 
                              "Select multiple countries and continents by holding down the `shift` key and clicking on them, click and drag to highlight a range of countries on any of the scatter plots.", 
                              "All interactive features could be combined with each other to carry out detailed and more complex explorations."])
).configure_title(
    align='center',
    anchor='middle'
)

# Save dashboard to HTML
dashboard.save('dashboard-1.html')