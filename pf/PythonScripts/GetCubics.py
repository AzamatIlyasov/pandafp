#! python3
# -*- coding: utf-8 -*-

"""
:author:       Vinzent Krausse (V.Krausse@digsilent.de)
:organization: DIgSILENT GmbH
:version:      001
:date:         2017-01-22
:short:        Get all cubicles.
:todo:         -
:description:  It has the same functionality like the DPL script "GetCubics.ComDpl".
:notes:
                 001 (AS): base functionality to collect all cubicles
"""
import powerfactory                     # @UnresolvedImport pylint: disable=import-error

from typing import Tuple


def Execute(pfApp: "powerfactory.Application"=None) -> Tuple[list, list, list]:
    """
    Get all cubicles.

    :param[in] pfApp:       The PowerFactory application.

    :return:                A tuple of sets: (aCubicsForEdgeMeas, aCubicsForNodeMeas, aCubicsForLoadingMeas).
    """
    # perhaps gets the PowerFactory application and the current script
    if not pfApp:
        pfApp = powerfactory.GetApplication()     # @UndefinedVariable

    # initialisation: clear all sets/maps
    aCubicsForEdgeMeas = []
    aCubicsForNodeMeas = []
    aCoups = []
    aLoadingElements = []
    aCubicsForLoadingMeas = []

    # iterate over all cubicles
    aAllCubics = pfApp.GetCalcRelevantObjects('StaCubic')
    for oCubic in aAllCubics:  # pylint: disable=too-many-nested-blocks
        # clear the description
        oCubic.desc = []

        # check, if the cubicle is connected
        oConnectedObject = oCubic.obj_id
        if not oConnectedObject:
            continue

        # add lnies (*.ElmLne) to aLoadingElements and aCubicsForLoadingMeas
        if oConnectedObject.GetClassName() == 'ElmLne':
            aCubicsForEdgeMeas.append(oCubic)
            if oCubic.obj_bus == 1:  # only on LV side
                if oConnectedObject not in aLoadingElements:
                    aLoadingElements.append(oConnectedObject)
                    aCubicsForLoadingMeas.append(oCubic)
        else:
            # add transformers (*.ElmTr2) to aLoadingElements and aCubicsForLoadingMeas
            if oConnectedObject.GetClassName() == 'ElmTr2':
                aCubicsForEdgeMeas.append(oCubic)
                if oCubic.obj_bus == 1:  # only on LV side
                    if oConnectedObject not in aLoadingElements:
                        aLoadingElements.append(oConnectedObject)
                        aCubicsForLoadingMeas.append(oCubic)
            else:
                # add couplers (*.ElmCoup) to aCoups and aCubicsForNodeMeas
                if oConnectedObject.GetClassName() == 'ElmCoup':
                    oTerminal = oCubic.GetParent()
                    if oTerminal.iUsage == 0:
                        if oTerminal not in aCoups:
                            aCoups.append(oTerminal)
                            aCubicsForNodeMeas.append(oCubic)

    # return
    return (aCubicsForEdgeMeas, aCubicsForLoadingMeas, aCubicsForNodeMeas)
