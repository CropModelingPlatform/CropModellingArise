DELETE FROM Coordinates;
INSERT INTO Coordinates
SELECT CAST(DemTemp.dem_average AS INTEGER) as altitude,
DemTemp.lat as latitudeDD,
DemTemp.lon as longitudeDD,
'' as codeSWstation,
DemTemp.lat || '_' || DemTemp.lon as idPoint,
'' as startRain,
'' as EndRain,
'' as SourceW,
'' as SourceRain,
'' as Comment,
'' as ev
FROM DemTemp
