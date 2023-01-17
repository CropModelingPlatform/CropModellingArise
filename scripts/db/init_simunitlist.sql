DELETE FROM Coordinate_years;
INSERT INTO Coordinate_years
SELECT distinct idPoint,
    year
FROM RAClimateD;
DELETE FROM SimUnitList;
INSERT INTO SimUnitList
SELECT Coordinate_years.idpoint || '_' || Coordinate_years.year || '_' || CropManagement.idMangt,
    Coordinate_years.Year as StartYear,
    100 as StartDay,
    Coordinate_years.Year as EndYear,
    360 as EndDay,
    Coordinate_years.idPoint,
    CropManagement.idMangt,
    Soil.IdSoil,
    1 as IdIni,
    1 as IdOption
FROM CropManagement,
    Soil,
    Coordinate_years
WHERE CropManagement.idMangt = 'Fert0'
    AND Soil.IdSoil = Coordinate_years.idpoint --WHERE Soil.IdSoil = Coordinate_years.idpoint
ORDER BY Coordinate_years.idPoint,
    CropManagement.idMangt,
    Soil.IdSoil,
    Coordinate_years.Year;