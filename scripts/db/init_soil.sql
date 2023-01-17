DELETE FROM Soil;
INSERT INTO Soil
SELECT SoilTemp.lat || '_' || SoilTemp.lon as IdSoil ,
'simple' as SoilOption,
'Loamy Sand' as SoilTextureType,
SoilTemp.SoilRDepth,
SoilTemp.SoilTotalDepth,
SoilTemp.OrganicNstock,
null as Slope,
1 as RunoffType,
SoilTemp.Wwp,
SoilTemp.Wfc,
SoilTemp.bd,
'0.3' as albedo,
SoilTemp.pH,
SoilTemp.OrganicC,
SoilTemp.cf
FROM SoilTemp