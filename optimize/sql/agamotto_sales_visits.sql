CREATE OR REPLACE TABLE `google.com:robsantos-agamotto.horus_info.agamotto_sales_visits` AS (
    WITH
       sales_table AS (
           SELECT 
             SUM(daily_sales_table.Vlr_Venda) as day_sales,
             daily_sales_table.Filial as store_id,
             DATE(Data) as day_time,
           FROM 
             `google.com:robsantos-agamotto.horus_info.store` as store_table
           INNER JOIN 
             `google.com:robsantos-agamotto.horus_info.sales` as daily_sales_table
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
          `google.com:robsantos-agamotto.horus_info.count` as daily_count_table
        INNER JOIN 
          `google.com:robsantos-agamotto.horus_info.stream` as stream_table
        ON  
          daily_count_table.id_stream = stream_table.id_stream
        INNER JOIN
          `google.com:robsantos-agamotto.horus_info.device` as device_table
        ON
          stream_table.mac_address = device_table.mac_address
        INNER JOIN
          `google.com:robsantos-agamotto.horus_info.store` as store_table
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