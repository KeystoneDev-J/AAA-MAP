import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from shapely.geometry import box

# Define the states each AAA covers
aaa_coverage = {
    'AAA - ACE Southern California': ['California'],
    'AAA East Central': ['Pennsylvania', 'Ohio', 'Kentucky', 'West Virginia', 'New York'],
    'Auto Club Group (ACG)': ['Colorado', 'Florida', 'Georgia', 'Illinois', 'Indiana', 'Iowa', 'Michigan', 'Minnesota', 'Nebraska', 'North Carolina', 'North Dakota', 'South Carolina', 'Tennessee', 'Wisconsin', 'Puerto Rico'],
    'CSAA Insurance Group': ['Arizona', 'Colorado', 'Connecticut', 'Delaware', 'Maryland', 'Montana', 'Nevada', 'Oklahoma', 'Oregon', 'South Dakota', 'Utah', 'Washington DC', 'Wyoming',
                             'California', 'Idaho', 'Indiana', 'Kansas', 'Kentucky', 'New Jersey', 'New York', 'Ohio', 'Pennsylvania', 'Virginia', 'West Virginia']
}

# Assign colors to each AAA, with CSAA as purple and complementary colors for others
colors = {
    'AAA - ACE Southern California': '#FFC300',  # yellow
    'AAA East Central': '#FF5733',  # orange
    'Auto Club Group (ACG)': '#3498DB',  # blue
    'CSAA Insurance Group': '#800080'  # purple
}

# State abbreviations for labeling
state_abbr = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS',
    'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA',
    'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT',
    'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM',
    'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
    'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD',
    'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
    'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY', 'Puerto Rico': 'PR', 'Washington DC': 'DC'
}

# Read the US states shapefile
gdf = gpd.read_file(r"C:\Users\jvonborstel_keystone\Desktop\QB Dev Projects\Map\AAA-MAP\ne_110m_admin_1_states_provinces.shp")

# Exclude Alaska and Hawaii
gdf = gdf[~gdf['name'].isin(['Alaska', 'Hawaii'])]

# Print all column names in the GeoDataFrame to identify the correct column for state names
print("Column names in GeoDataFrame:", gdf.columns)

# Use the 'name' column for state names
print("All available state names in GeoDataFrame:", gdf['name'].unique())

# Filter out non-US areas and keep only the states
gdf = gdf[gdf['name'].apply(lambda x: x in state_abbr.keys())]

# Debugging: Print out the names of the filtered states
print("Filtered states in GeoDataFrame:", gdf['name'].values)

# Map state names in GeoDataFrame to abbreviations
gdf['abbr'] = gdf['name'].map(state_abbr)

# Initialize a dictionary to keep track of states with multiple categories
state_categories = {state: [] for state in state_abbr.keys()}

# Assign categories to states
for aaa, states in aaa_coverage.items():
    for state in states:
        state_categories[state].append(aaa)

# Debugging: Print out the state categories dictionary
print("State categories:", state_categories)

# Create a figure and axis
fig, ax = plt.subplots(1, 1, figsize=(20, 15))

# Plot each state with the corresponding color or divided if it belongs to multiple categories
for state, categories in state_categories.items():
    if state in gdf['name'].values:
        if len(categories) > 0:
            if len(categories) == 1:
                gdf[gdf['name'] == state].plot(ax=ax, color=colors[categories[0]], edgecolor='black')
            else:
                state_geom = gdf[gdf['name'] == state].geometry.values[0]
                x_min, y_min, x_max, y_max = state_geom.bounds
                if state == 'California':
                    # Special case for California to cover the top half with purple
                    half_y = y_min + (y_max - y_min) / 2
                    top_geom = state_geom.intersection(box(x_min, half_y, x_max, y_max))
                    bottom_geom = state_geom.intersection(box(x_min, y_min, x_max, half_y))
                    top_gdf = gpd.GeoDataFrame(geometry=[top_geom], crs=gdf.crs)
                    bottom_gdf = gpd.GeoDataFrame(geometry=[bottom_geom], crs=gdf.crs)
                    top_gdf.plot(ax=ax, color=colors['CSAA Insurance Group'], edgecolor='black')
                    bottom_gdf.plot(ax=ax, color=colors['AAA - ACE Southern California'], edgecolor='black')
                else:
                    width = (x_max - x_min) / len(categories)
                    for i, category in enumerate(categories):
                        part_geom = state_geom.intersection(box(x_min + i * width, y_min, x_min + (i + 1) * width, y_max))
                        part_gdf = gpd.GeoDataFrame(geometry=[part_geom], crs=gdf.crs)
                        part_gdf.plot(ax=ax, color=colors[category], edgecolor='black')
        else:
            gdf[gdf['name'] == state].plot(ax=ax, color='none', edgecolor='black')

# Plot states without categories with just borders
states_with_categories = set([state for states in state_categories.values() for state in states])
gdf[~gdf['name'].isin(states_with_categories)].plot(ax=ax, color='none', edgecolor='black')

# Manually add Puerto Rico below Florida
puerto_rico_geom = gpd.GeoSeries(box(-80, 17, -70, 18))  # Adjusted the coordinates for a smaller box
puerto_rico_gdf = gpd.GeoDataFrame(geometry=puerto_rico_geom, crs=gdf.crs)
puerto_rico_gdf.plot(ax=ax, color=colors['Auto Club Group (ACG)'], edgecolor='black')
plt.text(-75, 17.5, 'PR', horizontalalignment='center', fontsize=10, fontweight='bold')

# Add state abbreviations
for idx, row in gdf.iterrows():
    plt.text(row['geometry'].centroid.x, row['geometry'].centroid.y, row['abbr'],
             horizontalalignment='center', fontsize=9, fontweight='bold')

# Create the legend
legend_elements = [Patch(facecolor=colors[aaa], edgecolor='black', label=aaa) for aaa in aaa_coverage.keys()]
plt.legend(handles=legend_elements, loc='lower left')

# Add a title
plt.title('AAA Insurance Coverage by State', fontsize=20)

# Remove the axis
ax.set_axis_off()

# Show the plot
plt.show()
