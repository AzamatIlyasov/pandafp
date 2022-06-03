#! python3
# -*- coding: utf-8 -*-

"""
:author:       Vinzent Krausse (V.Krausse@digsilent.de)
:organization: DIgSILENT GmbH
:version:      003
:date:         2019-01-09
:short:        Creates breaker measurements for all switches/couplers.
:todo:         -
:description:  It has the same functionality like the DPL script "CreateBreakerMeas.ComDpl".
:notes:
               001 (??): base functionality to create all external measurements for all switches/couplers
               002 (VK): re-factoring (rename variables and add description/comments)
               003 (AS): set foreign key for input
"""

import powerfactory                     # @UnresolvedImport pylint: disable=import-error

import ReplaceInvalidChars
import SetStatus


# pylint: disable=too-many-branches, too-many-locals, too-many-statements
def Execute(pfApp: "powerfactory.Application"=None, sTagPrefix: str='PF.', sSeparator: str=',', iDebug: int=0) -> int:
    """
    Creates breaker measurements for all switches (StaSwitch):
     * base name <BASE_NAME> = <SWITCH>_<VOLTAGE>kV_<TERMINAL>_<CUBICLE>
     * StaExtbrkmea as reader from OPC server:
        - use name:  <STATION>_<BASE_NAME>
        - use tag:   <TAG_PREFIX><STATION><SEPARATOR><BASE_NAME>_BK
     * StaExtdatmea as writer to OPC server:
        - use name:  Brk_<STATION>_<BASE_NAME>_Res
        - use tag:   <TAG_PREFIX><STATION><SEPARATOR><BASE_NAME>_BK_RES
    Creates breaker measurements for all couplers (ElmCoup):
     * base name <BASE_NAME> = <CB|Disc>_<VOLTAGE>kV_<TERMINAL>_<COUPLER>
     * StaExtbrkmea as reader from OPC server:
        - use name:  <STATION>_<BASE_NAME>
        - use tag:   <TAG_PREFIX><STATION><SEPARATOR><BASE_NAME>_BK
     * StaExtdatmea as writer to OPC server:
        - use name:  Brk_<STATION>_<BASE_NAME>_Res
        - use tag:   <TAG_PREFIX><STATION><SEPARATOR><BASE_NAME>_BK_RES

    :param[in] pfApp:       The PowerFactory application.
    :param[in] sTagPrefix:  The prefix of the generated measurement tag.
    :param[in] sSeparator:  Separator in the middle of the OPC tag.
    :param[in] iDebug:      Debug output: 0=no output; otherwise=output.

    :return:                The number of created measurement objects.
    """
    # perhaps gets the PowerFactory application and the current script
    if not pfApp:
        pfApp = powerfactory.GetApplication()     # @UndefinedVariable
    script = pfApp.GetCurrentScript()

    # initialise the counter
    iCounter = 0

    # add external measurements (StaExtbrkmea+StaExtdatmea) to all switches (StaSwitch)
    aBreakers = pfApp.GetCalcRelevantObjects('*.StaSwitch')
    for oBreaker in aBreakers:
        # get cubicle and terminal (incl. its names) of the breaker
        oCubicle = oBreaker.GetParent()
        oTerminal = oCubicle.GetParent()
        sTerminal = oTerminal.loc_name
        sCubicle = oCubicle.loc_name

        # get name of the station/busbar
        oStation = getattr(oBreaker, 'cpSite') if hasattr(oBreaker, 'cpSite') else None
        if not oStation:
            oStation = getattr(oBreaker, 'cpSubstat') if hasattr(oBreaker, 'cpSubstat') else None
        if oStation:
            sStation = oStation.loc_name
        else:
            sStation = oTerminal.loc_name

        dVoltage = oTerminal.uknom
        sBaseName = '%s_%dkV_%s_%s' % (oBreaker.loc_name, int(dVoltage + 0.5), sTerminal, sCubicle)

        # create measurement (StaExtbrkmea) for input.
        oStaExtMea = oCubicle.CreateObject('StaExtbrkmea', sStation, '_', sBaseName)
        if iDebug:
            pfApp.PrintInfo("%s - Create measurement %s in cubicle %s for breaker %s." % (script.loc_name, oStaExtMea, oCubicle, oBreaker))

        SetStatus.Execute(oStaExtMea, 1, 0)  # set status to read (OPC -> PF)
        oStaExtMea.pObject = oBreaker
        oStaExtMea.variabName = 'on_off'

        sTagId = '%s%s%s%s_BK' % (sTagPrefix, sStation, sSeparator, sBaseName)
        sTagId = ReplaceInvalidChars.Execute(sTagId)
        oStaExtMea.sTagID = sTagId
        oStaExtMea.for_name = sTagId

        iCounter += 1

        # create measurement (StaExtdatmea) for output
        oStaExtMea = oCubicle.CreateObject('StaExtdatmea', 'Brk_', sStation, '_', sBaseName, '_Res')
        if iDebug:
            pfApp.PrintInfo("%s - Create measurement %s in cubicle %s for breaker %s." % (script.loc_name, oStaExtMea, oCubicle, oBreaker))

        SetStatus.Execute(oStaExtMea, 0, 1)  # set status to write (PF -> OPC)
        oStaExtMea.pCalObj = oBreaker
        oStaExtMea.varCal = 'on_off'
        oStaExtMea.pCalObjSim = oBreaker
        oStaExtMea.varCalSim = 'on_off'
        oStaExtMea.i_dat = 1  # set type to integer

        sTagId += '_RES'
        oStaExtMea.sTagID = sTagId
        oStaExtMea.for_name = sTagId

        iCounter += 1

    # add external measurements (StaExtbrkmea+StaExtdatmea) to all couplers (ElmCoup)
    aBreakers = pfApp.GetCalcRelevantObjects('*.ElmCoup')
    for oBreaker in aBreakers:
        # get cubicle of the couplers
        oCubicle = oBreaker.GetCubicle(0)
        if not oCubicle:
            oCubicle = oBreaker.GetCubicle(1)
        if not oCubicle:
            continue

        # get nearest busbar
        oTerminal = oCubicle.GetParent()
        iRes = getattr(oTerminal, 'iUsage') if hasattr(oTerminal, 'iUsage') else None
        if iRes > 0:
            aConnectedBusbars, aConnectableBusbars = oCubicle.GetNearestBusbars(0)
            oTerminal = aConnectedBusbars[0] or aConnectableBusbars[0]

        # get name of the station
        oStation = getattr(oBreaker, 'cpSite') if hasattr(oBreaker, 'cpSite') else None
        if not oStation:
            oStation = getattr(oBreaker, 'cpSubstat') if hasattr(oBreaker, 'cpSubstat') else None
        if oStation:
            sStation = oStation.loc_name
        else:
            sStation = oTerminal.loc_name

        # get breaker class
        sCoupler = oBreaker.loc_name
        iRes = oBreaker.IsBreaker()
        if iRes:
            sBrkClass = 'CB'
        else:
            sBrkClass = 'Disc'

        dVoltage = oTerminal.uknom
        sBaseName = '%s_%dkV_%s' % (sBrkClass, int(dVoltage + 0.5), sCoupler)

        # create measurement (StaExtbrkmea) for input
        oStaExtMea = oCubicle.CreateObject('StaExtbrkmea', sStation, '_', sBaseName)
        if iDebug:
            pfApp.PrintInfo("%s - Create measurement %s in cubicle %s for breaker %s." % (script.loc_name, oStaExtMea, oCubicle, oBreaker))

        SetStatus.Execute(oStaExtMea, 1, 0)  # set status to read (OPC -> PF)
        oStaExtMea.pObject = oBreaker
        oStaExtMea.variabName = 'on_off'

        sTagId = '%s%s%s%s_BK' % (sTagPrefix, sStation, sSeparator, sBaseName)
        sTagId = ReplaceInvalidChars.Execute(sTagId)
        oStaExtMea.sTagID = sTagId
        oStaExtMea.for_name = sTagId

        iCounter += 1

        # Create measurement (StaExtdatmea) for output
        oStaExtMea = oCubicle.CreateObject('StaExtdatmea', 'Brk_', sStation, '_', sBaseName, '_Res')
        if iDebug:
            pfApp.PrintInfo("%s - Create measurement %s in cubicle %s for breaker %s." % (script.loc_name, oStaExtMea, oCubicle, oBreaker))

        SetStatus.Execute(oStaExtMea, 0, 1)    # set status to write (PF -> OPC)
        oStaExtMea.pCalObj = oBreaker
        oStaExtMea.varCal = 'on_off'
        oStaExtMea.pCalObjSim = oBreaker
        oStaExtMea.varCalSim = 'on_off'
        oStaExtMea.i_dat = 1  # set type to integer

        sTagId += '_RES'
        oStaExtMea.sTagID = sTagId
        oStaExtMea.for_name = sTagId

        iCounter += 1

    # debug output: summary
    if iDebug:
        pfApp.PrintInfo("%s - Create %d *.{StaExtbrkmea,StaExtdatmea} objects." % (script.loc_name, iCounter))

    # return the number of created measurements
    return iCounter


if __name__ == "__main__":
    PF_APP = powerfactory.GetApplication()     # @UndefinedVariable
    SCRIPT = PF_APP.GetCurrentScript()
    S_TAG_PREFIX = SCRIPT.sTagPrefix if hasattr(SCRIPT, 'sTagPrefix') else 'PF.'
    S_SEPARATOR = SCRIPT.sSeparator if hasattr(SCRIPT, 'sSeparator') else ','
    I_DEBUG = int(SCRIPT.iDebug) if hasattr(SCRIPT, 'iDebug') else 0
    Execute(PF_APP, S_TAG_PREFIX, S_SEPARATOR, I_DEBUG)
    PF_APP = None
