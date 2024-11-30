import pandas as pd
import numpy as np
import altair as alt
from altair import datum
import geopandas as gpd
from vega_datasets import data

df = pd.read_csv('world-data-2023_cleaned.csv')

continent_color_scale = alt.Scale(
    domain=['Asia', 'Europe', 'Africa', 'Americas', 'Oceania'],
    range=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
)


country_selection = alt.selection_point(
    fields=['country-code'],
    empty=False
    
    # nearest=True
)



continent_selection = alt.selection_point(
    fields=['region'],
    nearest=True
)

brush_selection = alt.selection_interval(
    encodings=['x', 'y']
)


# Update legend chart
legend = alt.Chart(df).transform_aggregate(
    groupby=['region']
).mark_point(size=100).encode(
    y=alt.Y('region:N', axis=alt.Axis(title=None, labelAngle=-90)),
    color=alt.Color('region:N', scale=continent_color_scale, legend=None),
    opacity=alt.condition(continent_selection & brush_selection, alt.value(1), alt.value(0.2)),
    fill=alt.Color('region:N', scale=continent_color_scale, legend=None),
    fillOpacity=alt.condition(country_selection & brush_selection, alt.value(0.8), alt.value(0.2))
).add_params(
    continent_selection, brush_selection
).properties(
    title='Continent'
)

sphere = alt.sphere()
graticule = alt.graticule()
# Layering and configuring the components
basemap = (
    alt.layer(
        #sphere background
        alt.Chart(sphere).mark_geoshape(fill='white'),
        #add meridians and parallels (graticules)
        alt.Chart(graticule).mark_geoshape(stroke='gray', strokeWidth=0.5),
    )   
)




# # Add continent borders
# continent_borders = alt.Chart(continent_map).mark_geoshape(
#     # stroke='black',  # Color of the continent borders
#     # strokeWidth=1.5,  # Thickness of the borders
#     # fillOpacity=0  # Ensure the fill is transparent
# ).transform_lookup(
#     lookup='id',
#     from_=alt.LookupData(
#         df,
#         'country-code',
#         ['region']  # Ensure the continent (region) data is included
#     )
# ).encode(
#     stroke=alt.condition(
#     continent_selection,
#     alt.Color('region:N'),
#     alt.value('lightgray')
# )
# ).project(
#     type='equalEarth'
# )



world_map = alt.topo_feature(data.world_110m.url, 'countries')

color_scheme = 'viridis'

projection_list = ['GDP per Capita', 'Life expectancy', 'CO2 Emissions per Capita', ]
projection_select = alt.binding_select(options=projection_list, name='World Map Metric:')
projection_param = alt.param(value='GDP per Capita', bind=projection_select)


choropleth = alt.Chart(world_map).mark_geoshape().encode(
    color=alt.Color('GDP per Capita:Q',
                 scale=alt.Scale(scheme=color_scheme),
                 title='GDP per Capita'),
    opacity=alt.condition(continent_selection & country_selection & brush_selection, alt.value(1), alt.value(0.3)),
    tooltip=[
        alt.Tooltip('Country:N', title='Country'),
        alt.Tooltip('GDP per Capita:Q', title='GDP per Capita'),
        alt.Tooltip('Life expectancy:Q', title='Life Expectancy'),
        alt.Tooltip('CO2 Emissions per Capita:Q', title='CO₂ Emissions per Capita')
    ]
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(
        df,
        'country-code',
        ['Country', 'GDP per Capita', 'Life expectancy', 'CO2 Emissions per Capita', 'country-code', 'region']
    )
).project(
    type='equalEarth'
).add_params(
    country_selection, brush_selection
).properties(
    width=900,
    height=540,
    title='GDP per Capita across the World'
) 




final_map = basemap + choropleth 

df_filtered = df[~df['Country'].isin(['Luxembourg', 'Liechtenstein'])]

# Update scatter plot
scatter_plot = alt.Chart(df_filtered).mark_point().encode(
    x=alt.X('GDP per Capita:Q', title='GDP per Capita'),
    y=alt.Y('Life expectancy:Q', title='Life Expectancy', scale=alt.Scale(domain=[df_filtered['Life expectancy'].min() - 5, df_filtered['Life expectancy'].max() + 5])),
    color=alt.Color( 'region:N', scale=continent_color_scale, legend=None),
    opacity=alt.condition(country_selection & brush_selection, alt.value(1), alt.value(0.25)),
    fill=alt.Color('region:N', scale=continent_color_scale, legend=None),
    fillOpacity=alt.condition(country_selection & brush_selection, alt.value(0.6), alt.value(0.2)),
    size=alt.Size('Population:Q', legend=None, scale=alt.Scale(range=[100, 3000]), title='Population'),
    order=alt.condition(country_selection, alt.value(1), alt.value(0)),
    tooltip=[
        alt.Tooltip('Country:N', title='Country'),
        alt.Tooltip('GDP per Capita:Q', title='GDP per Capita'),
        alt.Tooltip('Life expectancy:Q', title='Life Expectancy'),
        alt.Tooltip('Population:Q', title='Population'),
        alt.Tooltip('region:N', title='Continent')
    ]
).add_params(
    country_selection, brush_selection
).transform_filter(
    continent_selection
).properties(
    width=560,
    height=540,
    title='GDP per Capita vs Life Expectancy vs Population in Countries'
)

continent_avg_co2 = df.groupby('region').agg({'CO2 Emissions per Capita': 'mean'}).reset_index()

# Create bar chart for average CO2 emissions per continent
avg_co2_bar = alt.Chart(continent_avg_co2).mark_bar().encode(
    y=alt.Y('region:N', axis=alt.Axis(title='Continent')),
    x=alt.X('CO2 Emissions per Capita:Q', axis=alt.Axis(title='Average CO₂ Emissions per Capita')),
    color=alt.value('grey'),
    opacity=alt.condition(continent_selection & brush_selection, alt.value(0.4), alt.value(0.1)),
    tooltip=[
        alt.Tooltip('region:N', title='Continent'),
        alt.Tooltip('CO2 Emissions per Capita:Q', title='Average CO₂ Emissions per Capita')
    ]
).properties(
    width=640,
    height=540
).add_params(
    continent_selection
)

# remove qatar, trinidad and tobago
df_filtered = df[~df['Country'].isin(['Qatar', 'Trinidad and Tobago'])]

# Create scatter plot for individual country's CO2 emissions
country_co2_scatter = alt.Chart(df_filtered).mark_point(size=100).encode(
    y=alt.Y('region:N', axis=alt.Axis(title='Continent')),
    x=alt.X('CO2 Emissions per Capita:Q', axis=alt.Axis(title='CO₂ Emissions per Capita')),
    color=alt.Color('region:N', scale=continent_color_scale, legend=None),
    fill=alt.Color('region:N', scale=continent_color_scale, legend=None),
    fillOpacity=alt.condition(country_selection & brush_selection, alt.value(0.6), alt.value(0.2)),
    opacity=alt.condition(country_selection & brush_selection, alt.value(1), alt.value(0.25)),
    order=alt.condition(country_selection, alt.value(1), alt.value(0)),
    tooltip=[
        alt.Tooltip('Country:N', title='Country'),
        alt.Tooltip('CO2 Emissions per Capita:Q', title='CO₂ Emissions per Capita'),
        alt.Tooltip('region:N', title='Continent')
    ]
).add_params(
    country_selection, brush_selection
).transform_filter(
    continent_selection
)

# Overlay the scatter plot on top of the bar chart
emissions_chart = alt.layer(
    avg_co2_bar,
    country_co2_scatter
).resolve_scale(
    y='shared'
).properties(
    width=640,
    height=540,
    title='CO₂ Emissions per Capita across Countries and Continents'
)



health_indicators = [
    'Physicians per thousand',
    'Life expectancy',
    'Fertility Rate',
    'Infant mortality',
    'Maternal mortality ratio',
    'Out of pocket health expenditure'
]

df_health = df.dropna(subset=health_indicators)

parallel_data = df_health.melt(
    id_vars=['Country', 'country-code', 'region'],
    value_vars=health_indicators,
    var_name='Indicator',
    value_name='Value'
)

# Update parallel plot
parallel_plot = alt.Chart(parallel_data).transform_joinaggregate(
    min_value='min(Value)',
    max_value='max(Value)',
    groupby=['Indicator']
).transform_calculate(
    minmax_value='(datum.Value - datum.min_value) / (datum.max_value - datum.min_value)'
).mark_line(opacity=0.5).encode(
    x=alt.X('Indicator:N', title='Health Indicators', sort=health_indicators, axis=alt.Axis(labelAngle=-15)),
    y=alt.Y('minmax_value:Q', scale=alt.Scale(zero=False)),
    color=alt.Color('region:N', scale=continent_color_scale, legend=None),
    opacity=alt.condition(country_selection & brush_selection, alt.value(0.8), alt.value(0.05)),
    order=alt.condition(country_selection, alt.value(1), alt.value(0)),
    detail='country-code:N',
    tooltip=[
        alt.Tooltip('Country:N'),
        alt.Tooltip('Indicator:N'),
        alt.Tooltip('Value:Q')
    ]
).add_params(
    country_selection, brush_selection
).transform_filter(
    continent_selection
).properties(
    width=900,
    height=540,
    title='Health Indicators in Countries'
)


education_indicators = ['Gross primary education enrollment (%)', 'Gross tertiary education enrollment (%)']
df_education = df.dropna(subset=education_indicators)

# Calculate continent-wise average for education indicators
continent_avg_education = df_education.groupby('region').agg({
    'Gross primary education enrollment (%)': 'mean',
    'Gross tertiary education enrollment (%)': 'mean'
}).reset_index()

# Melt the dataframe for stacked bar chart
education_data = continent_avg_education.melt(
    id_vars=['region'],
    value_vars=education_indicators,
    var_name='Education Level',
    value_name='Rate'
)






# Create stacked bar chart for education rates
education_bar = alt.Chart(education_data).mark_bar().encode(
    x=alt.X('Rate:Q', axis=alt.Axis(title='Average Education Rate')),
    y=alt.Y('region:N', sort='-x', axis=alt.Axis(title='Continent')),
    color=alt.Color('Rate:Q', legend=None),
    opacity=alt.condition(continent_selection, alt.value(0.4), alt.value(0.1)),
).properties(
    width=640,
    height=540
)

# Filter out null values for unemployment rate
df_unemployment = df.dropna(subset=['Unemployment rate'])

# Create scatter plot for unemployment rate
unemployment_scatter = alt.Chart(df_unemployment).mark_point(size=100).encode(
    y=alt.Y('region:N', axis=alt.Axis(title='Continent')),
    x=alt.X('Unemployment rate:Q', axis=alt.Axis(title='Unemployment Rate')),
    color=alt.Color('region:N', scale=continent_color_scale, legend=None),
    fill=alt.Color('region:N', scale=continent_color_scale, legend=None),
    fillOpacity=alt.condition(country_selection & brush_selection, alt.value(0.6), alt.value(0.2)),
    opacity=alt.condition(country_selection & brush_selection, alt.value(1), alt.value(0.25)),
    order=alt.condition(country_selection, alt.value(1), alt.value(0)),
    tooltip=[
        alt.Tooltip('Country:N', title='Country'),
        alt.Tooltip('Gross primary education enrollment (%):Q', title='Primary Education Enrollment percentage'),
        alt.Tooltip('Gross tertiary education enrollment (%):Q', title='Tertiary Education Enrollment percentage'),
        alt.Tooltip('Unemployment rate:Q', title='Unemployment Rate'),
        # alt.Tooltip('region:N', title='Continent')
    ]
).add_params(
    country_selection, brush_selection
).transform_filter(
    continent_selection
)

# Combine the bar chart and scatter plot
education_unemployment_chart = alt.layer(
    education_bar,
    unemployment_scatter
).resolve_scale(
    x='independent'
).properties(
    width=640,
    height=540,
    title='Education and Unemployment in Countries and Continents' 
)

# Filter the data based on the selected country
selected_data = alt.Chart(df).transform_filter(
    country_selection
).transform_fold(
    ['Country', 'GDP per Capita', 'Life expectancy', 'CO2 Emissions per Capita', 'Population', 'Unemployment rate', 'CPI'], 
    as_=['Indicator', 'Value']
).mark_text().encode(
    y=alt.Y('Indicator:N', axis=alt.Axis(title=None, labelAngle=-75)),
    text=alt.Text('Value:N')
).properties(
    width=120,
    height=540,
    title='Country Statistics'
)


top_row = alt.hconcat(
    final_map.properties(width=900, height=540),
    selected_data.properties(width=120, height=540),
    parallel_plot.properties(width=900, height=540)
).resolve_scale(
    color='independent'
)


bottom_row = alt.hconcat(
    legend.properties(width=80, height=250),
    emissions_chart.properties(width=640, height=540),
    scatter_plot.properties(width=560, height=540),    
    education_unemployment_chart.properties(width=640, height=540),
).resolve_scale(
    color='independent'
)

dashboard = alt.vconcat(
    top_row,
    bottom_row
).properties(
    title='Socio-Economic and Health MCV'
)


dashboard.save('dashboard.html')