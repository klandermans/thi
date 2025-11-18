select 
   
    0.81*b_temp+5.60 as voorspelde_binnen_temperatuur,
   
    0.8*b_temp + b_rhi/100 * (b_temp - 14.4) + 46.4 as waargenomen_buiten_thi_weerstation,     
    0.8*(0.81*b_temp+5.60) + b_rhi/100 * ((0.81*b_temp+5.60) - 14.4) + 46.4 as berekende_binnen_thi_weerstation,     
   
    0.8*k_temp + k_RHI/100 * (k_temp - 14.4) + 46.4 as waargenomen_binnen_thi_koenders,
        
    0.8 * ( 0.81*t3+5.60)  + r3/100  * (( 0.81*t3+5.60)  - 14.4) + 46.4 voorspelde_berekende_binnen_thi_3hrs ,   
    0.8 * ( 0.81*t6+5.60)  + r6/100  * (( 0.81*t6+5.60)  - 14.4) + 46.4 voorspelde_berekende_binnen_thi_6hrs ,   
    0.8 * ( 0.81*t9+5.60)  + r9/100  * (( 0.81*t9+5.60)  - 14.4) + 46.4 voorspelde_berekende_binnen_thi_9hrs ,     
    0.8 * ( 0.81*t12+5.60) + r12/100 * (( 0.81*t12+5.60) - 14.4) + 46.4 voorspelde_berekende_binnen_thi_12hrs,  


    0.8 * t3  + r3/100  * (t3 - 14.4)  + 46.4 voorspelde_buiten_thi_3hrs ,   
    0.8 * t6  + r6/100  * (t6 - 14.4)  + 46.4 voorspelde_buiten_thi_6hrs ,   
    0.8 * t9  + r9/100  * (t9 - 14.4)  + 46.4 voorspelde_buiten_thi_9hrs ,   
    0.8 * t12 + r12/100 * (t12 - 14.4) + 46.4 voorspelde_buiten_thi_12hrs ,   
     
    
    *
    
from 

-- (
--     select 
--         [timestamp],
--         avg(temperature_150) as temperature_station
--     from (
--             select 
--                 CAST(DATEADD(SECOND, -DATEPART(SECOND, [timestamp]) - DATEPART(MINUTE, [timestamp]) * 60, [timestamp]) AS DATETIME ) AS [timestamp], 
--                 cast(temperature_150 as float)  as temperature_150
--             from t_raw_weerstation 
            
--     ) as asdf
--     group by 
--         [timestamp]
-- ) as tt

(
select
    CAST(DATEADD(SECOND, -DATEPART(SECOND, [datetime]) - DATEPART(MINUTE, [datetime]) * 60, [datetime]) AS DATETIME ) AS [timestamp], 
    cast(avg(k_temp) as int) as k_temp, 
    avg(temp_airkoe) as temp_airkoe,
    avg(k_rhi) as k_rhi, 
    cast(avg(b_temp) as int) as b_temp,
    avg(B_RHI) as B_RHI
    
    -- ,
    -- ,*
    -- avg(b_temp) -  (0.55 - 0.0055 * avg(B_RHI)) * (avg(b_temp) - 14.5) as b_thi,
    -- avg(k_temp) -  (0.55 - 0.0055 * avg(k_RHI)) * (avg(k_temp) - 14.5) as k_thi,
    -- avg(t3) -  (0.55 - 0.0055 * avg(r3)) * (avg(t3) - 14.5) as r3_thi


from (
    select 
        k.datetime, 
        hok,  
        k.temp as k_temp, 
        k.rhi as k_rhi, 
        temperature_150 as b_temp, 
        humidity_150 as b_rhi, 
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
   
    where 
        iif(hok='73', oost_73+west_73, iif(hok='72', oost_72+west_72, iif(hok='71', oost_71+west_71, iif(hok='70', oost_70+west_70, iif(hok='60', oost_60+west_60, 0) ) ) ) )  > 180

) as koenders
group by CAST(DATEADD(SECOND, -DATEPART(SECOND, [datetime]) - DATEPART(MINUTE, [datetime]) * 60, [datetime]) AS DATETIME ) 



) as kkk

left join  ( 
    select         
        tijd_nl,
        max(iif(vb<6, t,null)) as t3,
        max(iif(vb>6 and vb<12, t,null))   as t6,
        max(iif(vb>12 and vb<18, t,null))  as t9,
        max(iif(vb>18 and vb<24, t,null))  as t12,

        max(iif(vb<6, r,null)) as r3,
        max(iif(vb>6 and vb<12, r,null))   as r6,
        max(iif(vb>12 and vb<18, r,null))  as r9,
        max(iif(vb>18 and vb<24, r,null))  as r12


    from (
        SELECT  
            
            tijd_nl, 
            DATEADD(SECOND, [tijd], '1970-01-01') AT TIME ZONE 'UTC'     AT TIME ZONE 'W. Europe Standard Time' AS tijdv,
            -datediff(hh, tijd_nl, DATEADD(SECOND, [tijd], '1970-01-01') AT TIME ZONE 'UTC'     AT TIME ZONE 'W. Europe Standard Time'  ) as vb, 
            avg(cast(temp as float)) as t, 
            avg(cast(rv as float)) as r

        FROM 
            [dbo].[T_RAW_knmi_prediction]
        where 
            tijd_nl<getdate()
        group by  
            DATEADD(SECOND, [tijd], '1970-01-01') AT TIME ZONE 'UTC'     AT TIME ZONE 'W. Europe Standard Time' , tijd_nl
        having -datediff(hh, tijd_nl, DATEADD(SECOND, [tijd], '1970-01-01') AT TIME ZONE 'UTC'     AT TIME ZONE 'W. Europe Standard Time'  ) >0
        -- order by tijd_nl desc
        
    ) as asf
    -- where tijd_nl='2025-09-18 02:00:00.000'


    group by tijd_nl
    
) as pred on pred.tijd_nl=[timestamp]



-- select 



-- * from #tmp order by b_thi desc