
def get_agamotto_sales_visits_query(project, dataset):
    query_agamotto_sales_visits = """
      CREATE OR REPLACE TABLE `{project}.{dataset}.agamotto_sales_visits` AS (
          WITH
             sales_table AS (
                 SELECT 
                   SUM(daily_sales_table.Vlr_Venda) as day_sales,
                   daily_sales_table.Filial as store_id,
                   DATE(Data) as day_time,
                 FROM 
                   `{project}.{dataset}.store` as store_table
                 INNER JOIN 
                   `{project}.{dataset}.sales` as daily_sales_table
                 ON  
                   store_table.filial_key = daily_sales_table.Filial
                 GROUP BY 2,3
             ), 
             visits_table AS (
              SELECT 
                SUM(daily_count_table.count_in) as day_count,
                DATE(daily_count_table.starttime) as day_time,
                store_table.filial_key as store_id
              FROM 
                `{project}.{dataset}.count` as daily_count_table
              INNER JOIN 
                `{project}.{dataset}.stream` as stream_table
              ON  
                daily_count_table.id_stream = stream_table.id_stream
              INNER JOIN
                `{project}.{dataset}.device` as device_table
              ON
                stream_table.mac_address = device_table.mac_address
              INNER JOIN
                `{project}.{dataset}.store` as store_table
              ON
                device_table.branch = store_table.cnpj
              GROUP BY 2,3
             ),
             sales_visits_table AS (
               SELECT
                 sales_table.day_sales,
                 visits_table.day_count,
                 sales_table.day_time,
                 sales_table.store_id
               FROM sales_table
               INNER JOIN visits_table
               ON sales_table.store_id = visits_table.store_id
               WHERE 
               sales_table.day_time = visits_table.day_time
             )
             SELECT * FROM sales_visits_table
      );
    """.format(project=project, dataset=dataset)
    return query_agamotto_sales_visits


def get_agamotto_deltas_query(project, dataset):
    query_agamotto_deltas = """
    DECLARE table_7_interval DEFAULT 5;
    DECLARE table_14_interval DEFAULT 6;
    CREATE OR REPLACE TABLE `{project}.{dataset}.agamotto_deltas` AS (
          WITH
             sales_visits_7_table AS (
                SELECT 
                   SUM(day_sales) as week_7_sales,
                   SUM(day_count) as week_7_count,
                   store_id,
                   DATE_SUB(DATE_TRUNC(current_date(), WEEK(MONDAY)), INTERVAL table_7_interval WEEK) as start_7_week,
                   DATE_SUB(DATE_TRUNC(current_date(), WEEK(MONDAY)), INTERVAL table_7_interval-1 WEEK) as end_7_week,
                 FROM 
                   `{project}.{dataset}.agamotto_sales_visits`
                 WHERE
                   date(day_time) >= DATE_SUB(DATE_TRUNC(current_date(), WEEK(MONDAY)), INTERVAL table_7_interval WEEK)
                   AND date(day_time) <= DATE_SUB(DATE_TRUNC(current_date(), WEEK(MONDAY)), INTERVAL table_7_interval-1 WEEK)
                 GROUP BY
                   store_id
             ), 
             sales_visits_14_table AS (
                SELECT 
                   SUM(day_sales) as week_14_sales,
                   SUM(day_count) as week_14_count,
                   store_id,
                   DATE_SUB(DATE_TRUNC(current_date(), WEEK(SUNDAY)), INTERVAL table_14_interval WEEK) as start_14_week,
                   DATE_SUB(DATE_TRUNC(current_date(), WEEK(SUNDAY)), INTERVAL table_14_interval-1 WEEK) as end_14_week,
                 FROM 
                   `{project}.{dataset}.agamotto_sales_visits`
                 WHERE
                   date(day_time) >= DATE_SUB(DATE_TRUNC(current_date(), WEEK(SUNDAY)), INTERVAL table_14_interval WEEK)
                   AND date(day_time) <= DATE_SUB(DATE_TRUNC(current_date(), WEEK(SUNDAY)), INTERVAL table_14_interval-1 WEEK)
                 GROUP BY
                   store_id
             ),
             sales_visits_delta_table AS (
              SELECT 
                sales_visits_7_table.week_7_sales as week_7_sales,
                sales_visits_7_table.week_7_count as week_7_count,
                sales_visits_7_table.start_7_week as start_7_week,
                sales_visits_7_table.end_7_week as end_7_week,
                sales_visits_14_table.week_14_sales as week_14_sales,
                sales_visits_14_table.week_14_count as week_14_count,
                sales_visits_14_table.start_14_week as start_14_week,
                sales_visits_14_table.end_14_week as end_14_week,
                (sales_visits_7_table.week_7_sales - sales_visits_14_table.week_14_sales) as `delta_sales_wow`,
                (sales_visits_7_table.week_7_count - sales_visits_14_table.week_14_count) as `delta_count_wow`,
                (SAFE_DIVIDE((sales_visits_7_table.week_7_sales * 100) , sales_visits_14_table.week_14_sales)) as `delta_sales_wow_percentage`,
                (SAFE_DIVIDE((sales_visits_7_table.week_7_count * 100) , sales_visits_14_table.week_14_count)) as `delta_count_wow_percentage`,
                sales_visits_7_table.store_id
                FROM
                  sales_visits_7_table
                INNER JOIN
                  sales_visits_14_table
                ON 
                  sales_visits_7_table.store_id = sales_visits_14_table.store_id
             )
            SELECT * FROM sales_visits_delta_table
    );
    """.format(project=project, dataset=dataset)
    return query_agamotto_deltas