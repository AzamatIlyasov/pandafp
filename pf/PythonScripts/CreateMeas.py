#! python3
# -*- coding: utf-8 -*-

"""
:author:       Vinzent Krausse (V.Krausse@digsilent.de)
:organization: DIgSILENT GmbH
:version:      003
:date:         2019-01-09
:short:        Creates all required external measurement objects (StaExt*).
:todo:         -
:description:  It has the same functionality like the DPL script "CreateMeas.ComDpl".
:notes:
               001 (??): base functionality to create all external measurements
               002 (VK): re-factoring (rename variables and add description/comments)
               003 (AS): script to create description in cubicles for special measurements
"""

import powerfactory                     # @UnresolvedImport pylint: disable=import-error

import CreateBreakerMeas
import CreateCubicDesc
import CreateCubicMeas
import CreateGenLoadMeas
import CreateTapMeas
import DeleteMeas


# pylint: disable=too-many-arguments
def Execute(pfApp: "powerfactory.Application"=None, sTagPrefix: str='PF.', sSeparator: str=',', iCreateDesc: int=1,
            iCreateDatMeasForCont: int=1, iDebug: int=0) -> int:
    """
    Creates all required external measurement objects (StaExt*):
     1. Deletes all measurements (StaExt*) in active grid, see subscript DeleteMeas.ComDpl
     2. Creates breaker measurements (StaExtbrkmea and StaExtdatmea) for all switches/couplers,
        see subscript CreateBreakerMeas.ComDpl
     3. If iCreateDesc = 1 then creates description in cubicles of ElmLne, ElmTr2 and
        ElmCoup for special measurements.
     4. Creates P, Q, V measurements for special measurement points, see subscript CreateCubicMeas.ComDpl
     5. Creates measuemrents for all generators and loads, see subscript CreateGenLoadMeas.ComDpl
     6. Creates tap measuemrents for all transformers, see subscript CreateTapMeas.ComDpl

    :param[in] pfApp:       The PowerFactory application.
    :param[in] sTagPrefix:  The prefix of the generated measurement tag.
    :param[in] sSeparator:  Separator in the middle of the OPC tag.
    :param[in] iCreateDesc: Create description in cubicles of ElmLne, ElmTr2 and ElmCoup for special measurements
    :param[in] iCreateDatMeasForCont:  Create DAT-objects to write results of contingency analysis
    :param[in] iDebug:      Debug output: 0=no output; otherwise=output.

    :return:                The number of created measurement objects.
    """
    # perhaps gets the PowerFactory application and the current script
    if not pfApp:
        pfApp = powerfactory.GetApplication()   # @UndefinedVariable
    script = pfApp.GetCurrentScript()

    # initialise the counter
    iCounter = 0

    # deletes all measurements (StaExt*) in active grid
    DeleteMeas.Execute(pfApp)

    # creates breaker measurements (StaExtbrkmea and StaExtdatmea) for all switches/couplers
    iCounter += CreateBreakerMeas.Execute(pfApp, sTagPrefix, sSeparator)

    # create description for cubicles at ElmLne, ElmTr2 and ElmCoup to enable special measurement points
    if iCreateDesc:
        CreateCubicDesc.Execute(pfApp, iCreateDatMeasForCont)

    # creates P, Q, V measurements for special measurement points
    iCounter += CreateCubicMeas.Execute(pfApp, sTagPrefix, sSeparator)

    # creates external measurement (StaExtdatmea) for generators and loads
    iCounter += CreateGenLoadMeas.Execute(pfApp, sTagPrefix, sSeparator)

    # creates external measurements (StaExttapmea and StaExtdatmea) for all transformers
    iCounter += CreateTapMeas.Execute(pfApp, sTagPrefix, sSeparator)

    # debug output: summary
    if iDebug:
        pfApp.PrintInfo("%s - Create %d *.StaExt* objects." % (script.loc_name, iCounter))

    # return the number of created measurements
    return iCounter


if __name__ == "__main__":
    PF_APP = powerfactory.GetApplication()     # @UndefinedVariable
    SCRIPT = PF_APP.GetCurrentScript()
    S_TAG_PREFIX = SCRIPT.sTagPrefix if hasattr(SCRIPT, 'sTagPrefix') else 'PF.'
    S_SEPARATOR = SCRIPT.sSeparator if hasattr(SCRIPT, 'sSeparator') else ','
    I_CREATE_DESC = int(SCRIPT.iCreateDesc) if hasattr(SCRIPT, 'iCreateDesc') else 1
    I_CREATE_DAT_MEAS_FOR_CONT = int(SCRIPT.iCreateDatMeasForCont) if hasattr(SCRIPT, 'iCreateDatMeasForCont') else 1
    I_DEBUG = int(SCRIPT.iDebug) if hasattr(SCRIPT, 'iDebug') else 0
    Execute(PF_APP, S_TAG_PREFIX, S_SEPARATOR, I_CREATE_DESC, I_CREATE_DAT_MEAS_FOR_CONT, I_DEBUG)
    PF_APP = None
