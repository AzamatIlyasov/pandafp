#! python3
# -*- coding: utf-8 -*-

"""
:author:       Vinzent Krausse (V.Krausse@digsilent.de)
:organization: DIgSILENT GmbH
:version:      001
:date:         2019-01-22
:short:        Create a description in cubicles for measurement generation
:todo:         -
:description:  It has the same functionality like the DPL script "CreateCubicDesc.ComDpl".
:notes:
               001 (AS): base functionality to create descriptions in some cubicles
"""

import powerfactory                     # @UnresolvedImport pylint: disable=import-error

import GetCubics


def Execute(pfApp: "powerfactory.Application"=None, iCreateDatMeasForCont: int=1) -> int:
    """
    Create a description in cubicles for measurement generation:

    :param[in] pfApp:       The PowerFactory application.
    :param[in] iCreateDatMeasForCont:  If true then create loading descriptions for contingency analysis.

    :return:                The number of created measurement objects.
    """
    # perhaps gets the PowerFactory application and the current script
    if not pfApp:
        pfApp = powerfactory.GetApplication()     # @UndefinedVariable

    # get all cubicles
    aCubicsForEdgeMeas, aCubicsForLoadingMeas, aCubicsForNodeMeas = GetCubics.Execute(pfApp)

    # create description for Pmea and Qmea
    for oCubic in aCubicsForEdgeMeas:
        desc = oCubic.desc
        desc.insert(0, 'Pmea=io')
        desc.insert(1, 'Qmea=io')
        oCubic.desc = desc

    # perhaps create description for LoadingMea and maxLoadingMea
    if iCreateDatMeasForCont:
        for oCubic in aCubicsForLoadingMeas:
            desc = oCubic.desc
            desc.insert(2, 'LoadingMea=o')
            desc.insert(3, 'maxLoadingMea=o')
            oCubic.desc = desc

    # create description for Vmea, perhaps for VminMea and VmaxMea
    for oCubic in aCubicsForNodeMeas:
        desc = oCubic.desc
        desc.insert(0, 'Vmea=io')
        if iCreateDatMeasForCont:
            desc.insert(1, 'VminMea=o')
            desc.insert(2, 'VmaxMea=o')
        oCubic.desc = desc


if __name__ == "__main__":
    PF_APP = powerfactory.GetApplication()     # @UndefinedVariable
    SCRIPT = PF_APP.GetCurrentScript()
    I_CREATE_DAT_MEAS_FOR_CONT = int(SCRIPT.iCreateDatMeasForCont) if hasattr(SCRIPT, 'iCreateDatMeasForCont') else 1
    Execute(PF_APP, I_CREATE_DAT_MEAS_FOR_CONT)
    PF_APP = None
