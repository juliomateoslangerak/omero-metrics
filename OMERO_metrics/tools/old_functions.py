from OMERO_metrics.tools.data_preperation import (
    get_table_original_file_id,
)
import collections
import pandas as pd
import omero


def get_all_intensity_profiles(conn, data_df):
    df_01 = pd.DataFrame()
    for i, row in data_df.iterrows():
        file_id = (
            conn.getObject("FileAnnotation", row.Intensity_profiles)
            .getFile()
            .getId()
        )
        data = get_table_original_file_id(conn, str(file_id))
        for j in range(row.Channel):
            regx_find = f"ch0{j}"
            ch = i + j
            regx_repl = f"Ch0{ch}"
            data.columns = data.columns.str.replace(regx_find, regx_repl)
        df_01 = pd.concat([df_01, data], axis=1)
    return df_01


def get_table_file_id(conn, file_annotation_id):
    file_id = (
        conn.getObject("FileAnnotation", file_annotation_id).getFile().getId()
    )
    ctx = conn.createServiceOptsDict()
    ctx.setOmeroGroup("-1")
    r = conn.getSharedResources()
    t = r.openTable(omero.model.OriginalFileI(file_id), ctx)
    data_buffer = collections.defaultdict(list)
    heads = t.getHeaders()
    target_cols = range(len(heads))
    index_buffer = []
    num_rows = t.getNumberOfRows()
    for start in range(0, num_rows):
        data = t.read(target_cols, start, start)
        for col in data.columns:
            data_buffer[col.name] += col.values
        index_buffer += data.rowNumbers
    df = pd.DataFrame.from_dict(data_buffer)
    df.index = index_buffer[0 : len(df)]
    return df
