update SimUnitList set StartDay=(select sowingdate from CropManagement where idMangt='S19C1OF0IF0');
update SimUnitList set idIni=idPoint;