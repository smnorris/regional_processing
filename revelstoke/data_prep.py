# GCBM Preprocessing
# Imports


import os
import sys
import cPickle
import shutil
import logging

import archook
archook.get_arcpy()
import arcpy

sys.path.insert(0, '../../gcbm_preprocessing')
import preprocess_tools

import pgdata


def save_inputs():
    try:
        if not os.path.exists('inputs'):
            os.mkdir('inputs')
        cPickle.dump(inventory, open(r'inputs\inventory.pkl', 'wb'))
        cPickle.dump(historicFire1, open(r'inputs\historicFire1.pkl', 'wb'))
        cPickle.dump(historicFire2, open(r'inputs\historicFire2.pkl', 'wb'))
        cPickle.dump(historicHarvest, open(r'inputs\historicHarvest.pkl', 'wb'))
        cPickle.dump(historicInsect, open(r'inputs\historicInsect.pkl', 'wb'))
        cPickle.dump(
            rollbackDisturbances, open(r'inputs\rollbackDisturbances.pkl', 'wb')
        )
        cPickle.dump(spatialBoundaries, open(r'inputs\spatialBoundaries.pkl', 'wb'))
        cPickle.dump(NAmat, open(r'inputs\NAmat.pkl', 'wb'))
        cPickle.dump(transitionRules, open(r'inputs\transitionRules.pkl', 'wb'))
        cPickle.dump(yieldTable, open(r'inputs\yieldTable.pkl', 'wb'))
        cPickle.dump(AIDB, open(r'inputs\AIDB.pkl', 'wb'))
        cPickle.dump(resolution, open(r'inputs\resolution.pkl', 'wb'))
        cPickle.dump(rollback_enabled, open(r'inputs\rollback_enabled.pkl', 'wb'))
        cPickle.dump(historic_range, open(r'inputs\historic_range.pkl', 'wb'))
        cPickle.dump(rollback_range, open(r'inputs\rollback_range.pkl', 'wb'))
        cPickle.dump(future_range, open(r'inputs\future_range.pkl', 'wb'))
        cPickle.dump(activity_start_year, open(r'inputs\activity_start_year.pkl', 'wb'))
        cPickle.dump(
            inventory_raster_out, open(r'inputs\inventory_raster_out.pkl', 'wb')
        )
        cPickle.dump(tiler_scenarios, open(r'inputs\tiler_scenarios.pkl', 'wb'))
        cPickle.dump(GCBM_scenarios, open(r'inputs\GCBM_scenarios.pkl', 'wb'))
        cPickle.dump(tiler_output_dir, open(r'inputs\tiler_output_dir.pkl', 'wb'))
        cPickle.dump(
            recliner2gcbm_config_dir, open(r'inputs\recliner2gcbm_config_dir.pkl', 'wb')
        )
        cPickle.dump(
            recliner2gcbm_output_path,
            open(r'inputs\recliner2gcbm_output_path.pkl', 'wb'),
        )
        cPickle.dump(
            recliner2gcbm_exe_path, open(r'inputs\recliner2gcbm_exe_path.pkl', 'wb')
        )
        cPickle.dump(
            future_dist_input_dir, open(r'inputs\future_dist_input_dir.pkl', 'wb')
        )
        cPickle.dump(gcbm_raw_output_dir, open(r'inputs\gcbm_raw_output_dir.pkl', 'wb'))
        cPickle.dump(gcbm_configs_dir, open(r'inputs\gcbm_configs_dir.pkl', 'wb'))
        cPickle.dump(reportingIndicators, open(r'inputs\reportingIndicators.pkl', 'wb'))
        cPickle.dump(gcbm_exe, open(r'inputs\gcbm_exe.pkl', 'wb'))
        cPickle.dump(area_majority_rule, open(r'inputs\area_majority_rule.pkl', 'wb'))
    except:
        raise IOError("Failed to save inputs")


###############################################################################
#                            Required Inputs (BC)
#                                                     []: Restricting qualities
# Inventory [feature layer in geodatabase]
# Historic Fire Disturbances (NFDB, NBAC) [shapefiles where year is the last 4
#    characters before file extention]
# Historic Harvest Disturbances (BC Cutblocks) [shapefile]
# Historic Insect Disturbances [shapefiles where year is the last 4 characters
#    before file extention]
# Spatial Boundaries (TSA and PSPU) [shapefiles]
# NAmerica MAT (Mean Annual Temperature) [tiff]
# Yield Table (Growth Curves) [AIDB species matching column, classifier columns,
#    csv format]
# AIDB [pre-setup with disturbance matrix values etc.]
###############################################################################
if __name__ == "__main__":

    # Logging
    debug_log = r'logs\DebugLogDataPrep.log'
    if not os.path.exists(os.path.dirname(debug_log)):
        os.makedirs(os.path.dirname(debug_log))
    elif os.path.exists(debug_log):
        os.unlink(debug_log)
    logging.basicConfig(
        filename=debug_log,
        format='[%(asctime)s] %(levelname)s:%(message)s',
        level=logging.DEBUG,
        datefmt='%b%d %H:%M:%S',
    )
    # Variables
    province = "British Columbia"
    # TSA number as a string
    TSA_number = '27'
    # TSA name, replace spaces in the name with underscores
    TSA_name = 'Revelstoke'
    # directory path to the working directory for relative paths
    working_directory = r'Q:\projects\cat\2017_11_preprocessing\BC\TSA_{}_{}'.format(
        TSA_number, TSA_name
    )
    # directory path to the external data directory for relative paths
    external_data = r'Q:\projects\cat\2017_11_preprocessing\BC\00_external_data'
    # Tile resolution in degrees
    resolution = 0.001
    # The percent of harvest area slashburned in the Base scenario
    sb_percent = 50
    # Set true to enable rollback
    rollback_enabled = True
    # Set true for an area majority rule to be used in creating the gridded inventory
    # Set false for a centroid rule to be used (take attributes from the polygon at the
    # center of the grid cell)
    # The area majority rule is more robust but requires more memory and computing time
    area_majority_rule = False
    ## Year ranges
    historic_range = [1990, 2015]
    rollback_range = [1990, 2013]
    future_range = [2014, 2070]
    # Activity start year must be after historic range
    activity_start_year = 2018
    #### Spatial Inputs
    ## Inventory
    # Path the the inventory gdb workspace
    inventory_workspace = r"{}\01_spatial\02_inventory\Processed.gdb".format(
        external_data
    )
    # Layer name of the inventory in the gdb
    inventory_layer = "inventory"
    # The age field name in the inventory layer
    inventory_year = 2015
    # A dictionary with the classifiers as keys and the associated field names (as
    # they appear in the inventory) as values.
    inventory_classifier_attr = {"LdSpp": "LdSpp", "AU": "AU"}
    inventory_field_names = {
        "age": "Age2015",
        "species": "LdSpp",
        "THLB": "THLB",
        "THEME1": None,
        "THEME2": "AU",
        "THEME3": "LdSpp",
    }
    ## Disturbances
    # directory or geodatabase
    NFDB_workspace = r"{}\01_spatial\03_disturbances\01_historic\01_fire\shapefiles".format(
        external_data
    )
    # filter to get all layers within the directory/geodatabase, following glob syntax
    NFDB_filter = "NFDB*.shp"
    # the field from which the year can be extracted
    NFDB_year_field = "YEAR_"
    NBAC_workspace = r"{}\01_spatial\03_disturbances\01_historic\01_fire\shapefiles".format(
        external_data
    )
    NBAC_filter = "NBAC*.shp"
    NBAC_year_field = "EDATE"
    harvest_workspace = r"{}\01_spatial\03_disturbances\01_historic\02_harvest".format(
        external_data
    )
    harvest_filter = "BC_cutblocks90_15.shp"
    harvest_year_field = "HARV_YR"
    insect_workspace = r"{}\01_spatial\03_disturbances\01_historic\03_insect".format(
        external_data
    )
    insect_filter = "mpb*.shp"
    # directory path to the spatial reference directory containing the TSA and PSPU boundaries
    spatial_reference = r"{}\01_spatial\01_spatial_reference".format(external_data)
    # file name or filter to find the TSA boundaries in the spatial reference directory
    spatial_boundaries_tsa = "PSPUS_2016_FINAL_1_Reprojected.shp"
    # file name or filter to find the PSPU boundaries in the spatial reference directory
    spatial_boundaries_pspu = "PSPUS_2016.shp"
    # filter used to get the desired study area from the TSA boundaries.
    # change only the associated values for "field" and "code"
    study_area_filter = {"field": "TSA_NUMBER", "code": "'Cranbrook TSA'"}
    # field names for the Admin and Eco attributes in the PSPU boundaries file
    spatial_boundaries_attr = {"Admin": "AdminBou_1", "Eco": "EcoBound_1"}
    # path to NAmerica MAT (Mean Annual Temperature)
    NAmat_path = r"{}\01_spatial\04_environment\NAmerica_MAT_1971_2000.tif".format(
        external_data
    )
    ## Rollback Output
    # rolled back inventory output directory
    inventory_raster_out = r"{}\01a_pretiled_layers\02_inventory".format(
        working_directory
    )
    # rollback disturbances output file
    rollback_dist_out = r"{}\01a_pretiled_layers\03_disturbances\03_rollback\rollbackDist.shp".format(
        working_directory
    )
    # future disturbances input directory for woodstock
    future_dist_input_dir = r'{}\01a_pretiled_layers\03_disturbances\02_future\inputs'.format(
        working_directory
    )
    reprojected_redirection = ('01_spatial', '03_spatial_reprojected')
    clipped_redirection = (
        r'00_external_data\01_spatial',
        r'TSA_{}_{}\01a_pretiled_layers'.format(TSA_number, TSA_name),
    )
    ### Initialize Spatial Inputs
    inventory = preprocess_tools.inputs.Inventory(
        workspace=inventory_workspace,
        filter=inventory_layer,
        year=inventory_year,
        classifiers_attr=inventory_classifier_attr,
        field_names=inventory_field_names,
        province=province
    )
    historicFire1 = preprocess_tools.inputs.HistoricDisturbance(
        NFDB_workspace, NFDB_filter, NFDB_year_field
    )
    historicFire2 = preprocess_tools.inputs.HistoricDisturbance(
        NBAC_workspace, NBAC_filter, NBAC_year_field
    )
    historicHarvest = preprocess_tools.inputs.HistoricDisturbance(
        harvest_workspace, harvest_filter, harvest_year_field
    )
    historicInsect = preprocess_tools.inputs.HistoricDisturbance(
        insect_workspace, insect_filter, None
    )
    spatialBoundaries = preprocess_tools.inputs.SpatialBoundaries(
        spatial_reference,
        spatial_boundaries_tsa,
        spatial_boundaries_pspu,
        "shp",
        study_area_filter,
        spatial_boundaries_attr,
    )
    NAmat = preprocess_tools.inputs.NAmericaMAT(
        os.path.dirname(NAmat_path), os.path.basename(NAmat_path)
    )
    rollbackDisturbances = preprocess_tools.inputs.RollbackDisturbances(
        rollback_dist_out
    )
    external_spatial_data = [
        historicFire1,
        historicFire2,
        historicHarvest,
        historicInsect,
        NAmat,
        spatialBoundaries,
    ]
    # Warning: All spatial inputs that are not in WGS 1984 coordinate system need
    # to be reprojected
    #reproject = [
    # historicFire1, historicFire2, historicHarvest, historicInsect, NAmat, spatialBoundaries
    #]
    clip = [historicFire1, historicFire2, historicHarvest, historicInsect]
    copy = [sp for sp in external_spatial_data if sp not in clip]
    TSA_filter = '"{}" = {}'.format(
        study_area_filter["field"], study_area_filter["code"]
    )
    inventory.clipCutPolys(
        inventory.getWorkspace(),
        spatialBoundaries.getPath(),
        TSA_filter,
        r'{}\01a_pretiled_layers\00_Workspace.gdb'.format(working_directory),
        name='tsa{}'.format(TSA_number),
    )
    # for spatial_input in reproject:
    #    spatial_input.reproject(spatial_input.getWorkspace().replace(reprojected_redirection[0], reprojected_redirection[1]))

    # send inventory data to postgres
    # it may be faster to also clip with ogr2ogr but lets not bother for now
    # use the already clipped data rather than reworking the inventory object
    path = r'{}\01a_pretiled_layers\00_Workspace.gdb'.format(working_directory)
    layer = 'tsa{}'.format(TSA_number)
    db = pgdata.connect()
    db.ogr2pg(path, layer, 'inventory', t_srs='EPSG:4326')

    for spatial_input in clip:
        spatial_input.clip(
            spatial_input.getWorkspace(),
            spatialBoundaries.getPath(),
            TSA_filter,
            spatial_input.getWorkspace().replace(
                clipped_redirection[0], clipped_redirection[1]
            )
        )
    for spatial_input in copy:
        spatial_input.copy(
            spatial_input.getWorkspace().replace(
                clipped_redirection[0], clipped_redirection[1]
            )
        )
    ### Aspatial Inputs
    # Different scenarios to be run by the tiler (before Disturbance Matrix distinctions)
    # The scenario 'Base' must be included
    # Format: {<Scenario>: [<Slashburn Percent Base>, <Slashburn Percent After Actv>, <Harvest Percent After Actv>]}
    tiler_scenarios = {'Base': [sb_percent, sb_percent, 100]}
    # tiler_scenarios = {'Base':[sb_percent, sb_percent, 100],'B':[sb_percent, sb_percent, 98],'C':[sb_percent, sb_percent/2.0,100]}
    # GCBM scenarios (after Disturbance Matrix distinctions) with the associated tiler scenario as the key
    GCBM_scenarios = {'Base': 'Base'}
    # GCBM_scenarios = {'Base':'Base', 'A':'Base', 'B':'B', 'C':'C', 'D':'C'}
    ## Recliner2GCBM
    recliner2gcbm_config_dir = r"{}\02a_recliner2GCBM_input".format(working_directory)
    # create path
    os.makedirs(recliner2gcbm_config_dir)
    recliner2gcbm_output_path = r"{}\02b_recliner2GCBM_output\GCBMinput.db".format(
        working_directory
    )
    recliner2gcbm_exe_path = r"M:\Spatially_explicit\03_Tools\Recliner2GCBM-x64\Recliner2GCBM.exe"
    # directory where the tiler will output to
    tiler_output_dir = r"{}\01b_tiled_layers".format(working_directory)
    ## Yield table
    # path to yield table in external data
    original_yieldTable_path = r"{}\02_aspatial\02_yield_table\yield.csv".format(
        external_data
    )
    # path to the yield table (recommended to be in the recliner2gcbm config directory)
    yieldTable_path = r"{}\yield.csv".format(recliner2gcbm_config_dir)
    # The classifiers as keys and the column as value
    yieldTable_classifier_cols = {"AU": 0, "LdSpp": 1}
    # True if the first row of the yield table is a header
    yieldTable_header = True
    # year interval between age increments
    yieldTable_interval = 10
    # species column and increment range
    yieldTable_cols = {"SpeciesCol": 2, "IncrementRange": [3, 38]}
    ## AIDB
    # path to aidb in external data where disturbance matrix is already configured
    # according to scenario definitions
    original_aidb_path = r'{}\02_aspatial\01_AIDB\ArchiveIndex_Beta_Install_BASE.mdb'.format(
        external_data
    )
    # path to aidb
    aidb_path = r"{}\02a_recliner2GCBM_input\ArchiveIndex_Beta_Install_BASE.mdb".format(
        working_directory
    )
    ## Copy yield table and aidb

    shutil.copyfile(original_yieldTable_path, yieldTable_path)
    shutil.copyfile(original_aidb_path, aidb_path)
    ## GCBM Configuration
    # directory where the GCBM configuration JSON will be outputted
    gcbm_configs_dir = r'{}\04_run_GCBM\00_configs'.format(working_directory)
    # directory where GCBM will output the spatial data and output database to
    gcbm_raw_output_dir = '$output_dir'
    # paths to the tiled layers of any extra reporting indicators. these would be in
    # addition to the classifiers and eco boundary as reporting indicators
    reporting_indicators = {
        "ProtectedAreas": r"{}\01_spatial\05_reporting_indicators\protectedAreas_moja".format(
            external_data
        ),
        "THLB": None,
    }
    gcbm_exe = r'm:\spatially_explicit\03_tools\gcbm\moja.cli.exe'
    ### Initialize Aspatial Inputs
    yieldTable = preprocess_tools.inputs.YieldTable(
        path=yieldTable_path,
        classifier_cols=yieldTable_classifier_cols,
        header=yieldTable_header,
        interval=yieldTable_interval,
        cols=yieldTable_cols,
    )
    AIDB = preprocess_tools.inputs.AIDB(path=aidb_path)
    transitionRules = None
    reportingIndicators = preprocess_tools.inputs.ReportingIndicators(
        reporting_indicators
    )
    save_inputs()
