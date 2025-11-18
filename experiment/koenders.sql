
-- ALTER view [dbo].[VL_Totaal_koenders] as 
-- select datetime, hok, 
-- avg(temp) as temp,


--  avg(rhi) as rhi, meetsysteem
-- from 
-- (
--     select distinct 
--         datetime, 
--         hok, 
--         [value]-40 as temp, 
--         null as rhi, 
--         T_Raw_Koenders_mV_sensors.meetsysteem
--     from 
--         T_Raw_Koenders_mV_sensors 
--     left join 
--         T_Raw_Koenders_mV_sensors_keys on T_Raw_Koenders_mV_sensors.[index]=T_Raw_Koenders_mV_sensors_keys.[index] 
--     and T_Raw_Koenders_mV_sensors.field=T_Raw_Koenders_mV_sensors_keys.field
--     where [type]='temp'
--         and hok is not null
--         and [value] > 0
--         and [value] < 80
--     union all 
--     select distinct 
--         datetime, 
--         hok, null as temp, 
--         [value] as rhi, 
--         T_Raw_Koenders_mV_sensors.meetsysteem
--     from 
--         T_Raw_Koenders_mV_sensors 
--     left join 
--         T_Raw_Koenders_mV_sensors_keys on T_Raw_Koenders_mV_sensors.[index]=T_Raw_Koenders_mV_sensors_keys.[index] 
--     and T_Raw_Koenders_mV_sensors.field=T_Raw_Koenders_mV_sensors_keys.field
--     where [type]='rhi' and [value] > 0  and [value] < 100 and hok is not null
    
-- ) as tot
-- -- where 
--     -- datetime='2025-09-15 15:45:00.000'
-- where hok<>'62'
-- group by 
--     hok, 
--     datetime, 
--     meetsysteem



-- select * 
-- from 
-- T_Raw_Koenders_mV_sensors_keys

select 
    k.datetime, 
    hok,  
    k.temp as k_temp, 
    k.rhi as k_rhi, 
    temperature_150 as b_temp, 
    g.buitentemperatuur as b_a_temp, 
    iif(hok='73', temp_73, iif(hok='72', temp_72, iif(hok='71', temp_71, iif(hok='70', temp_70, iif(hok='60', temp_60, 0) ) ) ) ) as temp_airkoe,
    iif(hok='73', oost_73+west_73, iif(hok='72', oost_72+west_72, iif(hok='71', oost_71+west_71, iif(hok='70', oost_70+west_70, iif(hok='60', oost_60+west_60, 0) ) ) ) ) as gordijnen
    
    
from 
    vl_totaal_koenders as k 
left join (
    select     
        DATEADD(
            MINUTE,
            DATEDIFF(MINUTE, 0,timestamp ) / 15 * 15,
            0
        ) AS tt, * 
    from 
        t_raw_weerstation 
) as w  on cast(k.datetime as datetime)=tt
left join (
    select     
        DATEADD(
            MINUTE,
            DATEDIFF(MINUTE, 0, datum) / 15 * 15,
            0
        ) AS gg, * 
    from t_raw_gordijnen 
) as g  on cast(k.datetime as datetime)=gg
left join (  

    SELECT  
        DATEADD(SECOND, [tijd], '1970-01-01') AT TIME ZONE 'UTC'     AT TIME ZONE 'W. Europe Standard Time' AS tijdv,
        tijd_nl, 
        -datediff(hh, tijd_nl, DATEADD(SECOND, [tijd], '1970-01-01') AT TIME ZONE 'UTC'     AT TIME ZONE 'W. Europe Standard Time'  ) as vb, 
        avg(cast(temp as float)) as t, 
        avg(cast(rv as float)) as r
    FROM 
        [dbo].[T_RAW_knmi_prediction]
    group by  
          DATEADD(SECOND, [tijd], '1970-01-01') AT TIME ZONE 'UTC'     AT TIME ZONE 'W. Europe Standard Time' , tijd_nl


) as v on tijd_nl=[datetime]
where 
    iif(hok='73', oost_73+west_73, iif(hok='72', oost_72+west_72, iif(hok='71', oost_71+west_71, iif(hok='70', oost_70+west_70, iif(hok='60', oost_60+west_60, 0) ) ) ) )  > 180
    and datetime='2025-09-24 08:00:00.000'
    and hok='70'
order by 
    k.datetime desc


