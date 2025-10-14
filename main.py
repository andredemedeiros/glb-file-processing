from src.utils import load_glb, geometry_data_extract, meta_data_extract, raster_xy, slice_z, raster_xy_with_depth_color 

if __name__ == "__main__":
    scene = load_glb()
    geometries = geometry_data_extract(scene)
    print(geometries)

    print("\n--- Metadados da Cena ---")    
    meta_data_extract()

    print("\n--- Visualization ---")
    #mesh,scene = raster_xy(geometries)
    mesh,scene = raster_xy_with_depth_color(geometries)

    #slice_z(mesh)
