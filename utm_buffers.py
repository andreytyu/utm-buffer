import geopandas as gpd
import pyproj
from shapely.ops import transform

def project_to_from(geom, epsg1, epsg2):
    """Projects a shapely.geometry object from one CRS to another
    
    Args:
        geom (shapely.geometry object): geometry to be projected
        epsg1 (int): source CRS EPSG code
        epsg2 (int): output CRS EPSG code
        
    Returns:
        shapely.geometry object: input geometry projected to desired CRS
    """
    project = pyproj.Transformer.from_proj(
        pyproj.Proj('EPSG:{}'.format(epsg1)),
        pyproj.Proj('EPSG:{}'.format(epsg2)),
        always_xy=True)
    return transform(project.transform, geom)

def utm_buffers(gdf, buffer_size):
    """Creates buffer zones of given size for each geometry in the
    input geopandas.GeoDataFrame in it's UTM zone
    
    Args:
        gdf (geopandas.GeoDataFrame): geometry to be projectes
        buffer_size (int): desired buffer size in meters
        
    Returns:
        geopandas.GeoSeries: GeoSeries containing buffer zones
    """
    rep_points = gdf['geometry'].representative_point()
    lons = [geom.x for geom in rep_points]
    lats = [geom.y for geom in rep_points]
    utm_zones = [int(32700-round((45+lat)/90,0)*100+round((183+lon)/6,0)) for lat,lon in zip(lons,lats)]
    buffers = [project_to_from(
        project_to_from(
            pol,4326,epsg
        ).buffer(buffer_size),epsg,4326
    ) for pol,epsg in zip(gdf['geometry'], utm_zones)]
    
    return gpd.GeoSeries(buffers)

df = gpd.read_file('sample_data.geojson')
df['geometry'] = utm_buffers(df, 200)