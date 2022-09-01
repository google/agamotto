DECLARE table_7_interval DEFAULT 3;
DECLARE table_14_interval DEFAULT 4;
CREATE OR REPLACE TABLE `google.com:robsantos-agamotto.horus_info.agamotto_deltas` AS (
      WITH
         sales_visits_7_table AS (
            SELECT 
               SUM(day_sales) as week_7_sales,
               SUM(day_count) as week_7_count,
               store_id,
               DATE_SUB(DATE_TRUNC(current_date(), WEEK(MONDAY)), INTERVAL table_7_interval WEEK) as start_7_week,
               DATE_SUB(DATE_TRUNC(current_date(), WEEK(MONDAY)), INTERVAL table_7_interval-1 WEEK) as end_7_week,
             FROM 
               `google.com:robsantos-agamotto.horus_info.agamotto_sales_visits`
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
               `google.com:robsantos-agamotto.horus_info.agamotto_sales_visits`
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