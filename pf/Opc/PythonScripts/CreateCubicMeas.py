#! python3
# -*- coding: utf-8 -*-

"""
:author:       Vinzent Krausse (V.Krausse@digsilent.de)
:organization: DIgSILENT GmbH
:version:      003
:date:         2019-01-09
:short:        Creates measurements in cubicles according to cubdescription.
:todo:         -
:description:  It has the same functionality like the DPL script "CreateCubicMeas.ComDpl".
:notes:
               001 (??): base functionality to create all external measurements in special cubicles
               002 (VK): re-factoring (rename variables and add description/comments)
               003 (AS): consider contingency analysis results for output (VmaxMea, VminMea, Loading, maxLoading)
"""

import powerfactory                     # @UnresolvedImport pylint: disable=import-error

import IsContainedInDesc
import ReplaceInvalidChars
import SetStatus


# pylint: disable=too-many-branches, too-many-locals, too-many-statements
def Execute(pfApp: "powerfactory.Application"=None, sTagPrefix: str='PF.', sSeparator: str=',', iAbsoluteValues: int=1,
            iDebug: int=0) -> int:
    """
    Creates measurements in cubicles (StaCubic) according to cubdescription:
     * base name <BASE_NAME> = <COMPONENT_CLASS>_<VOLTAGE>kV_<COMPONENT_NAME>
     * StaExtpmea for cubicle's P input ("Pmea=i" in description):
        - use name:  P_<STATION>_<BASE_NAME>
        - use tag:   <TAG_PREFIX><STATION><SEPARATOR><BASE_NAME>_P
     * StaExtdatmea for cubicle's P output ("Pmea=o" in description):
        - use name:  P_<STATION>_<BASE_NAME>_Res
        - use tag:   <TAG_PREFIX><STATION><SEPARATOR><BASE_NAME>_P_RES
     * StaExtpmea for cubicle's Q input ("Qmea=i" in description):
        - use name:  Q_<STATION>_<BASE_NAME>
        - use tag:   <TAG_PREFIX><STATION><SEPARATOR><BASE_NAME>_Q
     * StaExtdatmea for cubicle's Q output ("Qmea=o" in description):
        - use name:  Q_<STATION>_<BASE_NAME>_Res
        - use tag:   <TAG_PREFIX><STATION><SEPARATOR><BASE_NAME>_Q_RES
     * StaExtpmea for cubicle's V input ("Vmea=i" in description):
        - use name:  V_<STATION>_<BASE_NAME>
        - use tag:   <TAG_PREFIX><STATION><SEPARATOR><BASE_NAME>_V
     * StaExtdatmea for cubicle's V output ("Vmea=o" in description):
        - use name:  V_<STATION>_<BASE_NAME>_Res
        - use tag:   <TAG_PREFIX><STATION><SEPARATOR><BASE_NAME>_V_RES
     * StaExtpmea for cubicle's VminMea output ("VminMea=o" in description):
        - use name:  Vmin_<STATION>_<BASE_NAME>_Res
        - use tag:   <TAG_PREFIX><STATION><SEPARATOR><BASE_NAME>_VMIN_RES
     * StaExtpmea for cubicle's VmaxMea output ("VmaxMea=o" in description):
        - use name:  Vmax_<STATION>_<BASE_NAME>_Res
        - use tag:   <TAG_PREFIX><STATION><SEPARATOR><BASE_NAME>_VMAX_RES
     * StaExtpmea for cubicle's LoadingMea output ("LoadingMea=o" in description):
        - use name:  Ld_<STATION>_<BASE_NAME>_Res
        - use tag:   <TAG_PREFIX><STATION><SEPARATOR><BASE_NAME>_LD_RES
     * StaExtpmea for cubicle's maxLoadingMea output ("maxLoadingMea=o" in description):
        - use name:  MxL_<STATION>_<BASE_NAME>_Res
        - use tag:   <TAG_PREFIX><STATION><SEPARATOR><BASE_NAME>_MXL_RES

    :param[in] pfApp:       The PowerFactory application.
    :param[in] sTagPrefix:  The prefix of the generated measurement tag.
    :param[in] sSeparator:  Separator in the middle of the OPC tag.
    :param[in] iAbsoluteValues:  0=p.u.; 1=absolute values of voltage for min and max voltage used
    :param[in] iDebug:      Debug output: 0=no output; otherwise=output.

    :return:                The number of created measurement objects.
    """
    # perhaps gets the PowerFactory application and the current script
    if not pfApp:
        pfApp = powerfactory.GetApplication()     # @UndefinedVariable
    script = pfApp.GetCurrentScript()

    # initialise the counter
    iCounter = 0

    # add external measurements (StaExtdatmea) to all cubicles (StaCubic) that contains Pmea, Qmea, Vmea in desc
    aCubicles = pfApp.GetCalcRelevantObjects('*.StaCubic')
    for oCubicle in aCubicles:
        # get component and terminal
        oComponent = oCubicle.obj_id
        if not oComponent:
            continue
        oTerminal = oCubicle.GetParent()
        dVoltage = oTerminal.uknom

        # get nearest busbar
        iRes = getattr(oTerminal, 'iUsage') if hasattr(oTerminal, 'iUsage') else None
        if iRes > 0:
            aConnectedBusbars, aConnectableBusbars = oCubicle.GetNearestBusbars(0)
            oTerminal = aConnectedBusbars[0] or aConnectableBusbars[0]

        oStation = getattr(oTerminal, 'cpSite') if hasattr(oTerminal, 'cpSite') else None
        if not oStation:
            oStation = getattr(oTerminal, 'cpSubstat') if hasattr(oTerminal, 'cpSubstat') else None
        if oStation:
            sStation = oStation.loc_name
        else:
            sStation = oTerminal.loc_name

        sClassName = oComponent.GetClassName()
        if sClassName == 'ElmCoup':
            sClassName = 'Bus'
            oComponent = oTerminal
        else:
            sClassName = sClassName[3:]

        # prepare tag name
        sBaseName = '%s_%dkV_%s' % (sClassName, int(dVoltage + 0.5), oComponent.loc_name)
        sBaseTag = sBaseName

        resList = IsContainedInDesc.Execute(oCubicle, 'Pmea')
        if resList[0]:
            # create P measurement (StaExtpmea) for P input
            if resList[1]:
                oStaExtMea = oCubicle.CreateObject('StaExtpmea', 'P_', sStation, '_', sBaseName)
                if iDebug:
                    pfApp.PrintInfo("%s - Create measurement %s in cubicle %s." % (script.loc_name, oStaExtMea, oCubicle))

                SetStatus.Execute(oStaExtMea, 1, 0)    # set status to read (OPC -> PF)
                oStaExtMea.Snom = 100  # default rating

                sTagId = '%s%s%s%s_P' % (sTagPrefix, sStation, sSeparator, sBaseTag)
                sTagId = ReplaceInvalidChars.Execute(sTagId)
                oStaExtMea.sTagID = sTagId
                oStaExtMea.for_name = sTagId

                iCounter += 1

            # create measurement (StaExtdatmea) for P output
            if resList[2]:
                oStaExtMea = oCubicle.CreateObject('StaExtdatmea', 'P_', sStation, '_', sBaseName, '_Res')
                if iDebug:
                    pfApp.PrintInfo("%s - Create measurement %s in cubicle %s." % (script.loc_name, oStaExtMea, oCubicle))

                SetStatus.Execute(oStaExtMea, 0, 1)    # set status to write (PF -> OPC)
                sVariable = ('m:P:%d' % (oCubicle.obj_bus))
                oStaExtMea.pCalObj = oComponent
                oStaExtMea.varCal = sVariable
                oStaExtMea.pCalObjSim = oComponent
                oStaExtMea.varCalSim = sVariable
                oStaExtMea.i_dat = 3    # set type to real

                sTagId = '%s%s%s%s_P_RES' % (sTagPrefix, sStation, sSeparator, sBaseTag)
                sTagId = ReplaceInvalidChars.Execute(sTagId)
                oStaExtMea.sTagID = sTagId
                oStaExtMea.for_name = sTagId

                iCounter += 1

        resList = IsContainedInDesc.Execute(oCubicle, 'Qmea')
        if resList[0]:
            # create Q measurement (StaExtqmea) for Q input
            if resList[1]:
                oStaExtMea = oCubicle.CreateObject('StaExtqmea', 'Q_', sStation, '_', sBaseName)
                if iDebug:
                    pfApp.PrintInfo("%s - Create measurement %s in cubicle %s." % (script.loc_name, oStaExtMea, oCubicle))

                SetStatus.Execute(oStaExtMea, 1, 0)    # set status to read (OPC -> PF)
                oStaExtMea.Snom = 100  # default rating

                sTagId = '%s%s%s%s_Q' % (sTagPrefix, sStation, sSeparator, sBaseTag)
                sTagId = ReplaceInvalidChars.Execute(sTagId)
                oStaExtMea.sTagID = sTagId
                oStaExtMea.for_name = sTagId

                iCounter += 1

            # create measurement (StaExtdatmea) for Q output
            if resList[2]:
                oStaExtMea = oCubicle.CreateObject('StaExtdatmea', 'Q_', sStation, '_', sBaseName, '_Res')
                if iDebug:
                    pfApp.PrintInfo("%s - Create measurement %s in cubicle %s." % (script.loc_name, oStaExtMea, oCubicle))

                SetStatus.Execute(oStaExtMea, 0, 1)    # set status to write (PF -> OPC)
                sVariable = ('m:Q:%d' % (oCubicle.obj_bus))
                oStaExtMea.pCalObj = oComponent
                oStaExtMea.varCal = sVariable
                oStaExtMea.pCalObjSim = oComponent
                oStaExtMea.varCalSim = sVariable
                oStaExtMea.i_dat = 3    # set type to real

                sTagId = '%s%s%s%s_Q_RES' % (sTagPrefix, sStation, sSeparator, sBaseTag)
                sTagId = ReplaceInvalidChars.Execute(sTagId)
                oStaExtMea.sTagID = sTagId
                oStaExtMea.for_name = sTagId

                iCounter += 1

        resList = IsContainedInDesc.Execute(oCubicle, 'Vmea')
        if resList[0]:
            # create V measurement (StaExtvmea) for V input
            if resList[1]:
                oStaExtMea = oCubicle.CreateObject('StaExtvmea', 'V_', sStation, '_', sBaseName)
                if iDebug:
                    pfApp.PrintInfo("%s - Create measurement %s in cubicle %s." % (script.loc_name, oStaExtMea, oCubicle))

                SetStatus.Execute(oStaExtMea, 1, 0)    # set status to read (OPC -> PF)

                sTagId = '%s%s%s%s_V' % (sTagPrefix, sStation, sSeparator, sBaseTag)
                sTagId = ReplaceInvalidChars.Execute(sTagId)
                oStaExtMea.sTagID = sTagId
                oStaExtMea.for_name = sTagId

                iCounter += 1

            # create measurement (StaExtdatmea) for V output
            if resList[2]:
                oStaExtMea = oCubicle.CreateObject('StaExtdatmea', 'V_', sStation, '_', sBaseName, '_Res')
                if iDebug:
                    pfApp.PrintInfo("%s - Create measurement %s in cubicle %s." % (script.loc_name, oStaExtMea, oCubicle))

                SetStatus.Execute(oStaExtMea, 0, 1)    # set status to write (PF -> OPC)
                oStaExtMea.pCalObj = oTerminal
                oStaExtMea.varCal = 'm:Ul'
                oStaExtMea.pCalObjSim = oTerminal
                oStaExtMea.varCalSim = 'm:Ul'
                oStaExtMea.i_dat = 3    # set type to real

                sTagId = '%s%s%s%s_V_RES' % (sTagPrefix, sStation, sSeparator, sBaseTag)
                sTagId = ReplaceInvalidChars.Execute(sTagId)
                oStaExtMea.sTagID = sTagId
                oStaExtMea.for_name = sTagId

                iCounter += 1

        resList = IsContainedInDesc.Execute(oCubicle, 'VminMea')
        if resList[0]:
            # create measurement (StaExtdatmea) for Vmin output
            if resList[2]:
                oStaExtMea = oCubicle.CreateObject('StaExtdatmea', 'Vmin_', sStation, '_', sBaseName, '_Res')
                if iDebug:
                    pfApp.PrintInfo("%s - Create measurement %s in cubicle %s." % (script.loc_name, oStaExtMea, oCubicle))

                if iAbsoluteValues:
                    oStaExtMea.Multip = 1/dVoltage
                SetStatus.Execute(oStaExtMea, 0, 1)    # set status to write (PF -> OPC)
                oStaExtMea.pCalObj = oTerminal
                oStaExtMea.varCal = 'm:min_v'
                oStaExtMea.pCalObjSim = oTerminal
                oStaExtMea.varCalSim = 'm:min_v'
                oStaExtMea.i_dat = 3    # set type to real

                sTagId = '%s%s%s%s_VMIN_RES' % (sTagPrefix, sStation, sSeparator, sBaseTag)
                sTagId = ReplaceInvalidChars.Execute(sTagId)
                oStaExtMea.sTagID = sTagId
                oStaExtMea.for_name = sTagId

                iCounter += 1

        resList = IsContainedInDesc.Execute(oCubicle, 'VmaxMea')
        if resList[0]:
            # create measurement (StaExtdatmea) for Vmax output
            if resList[2]:
                oStaExtMea = oCubicle.CreateObject('StaExtdatmea', 'Vmax_', sStation, '_', sBaseName, '_Res')
                if iDebug:
                    pfApp.PrintInfo("%s - Create measurement %s in cubicle %s." % (script.loc_name, oStaExtMea, oCubicle))

                if iAbsoluteValues:
                    oStaExtMea.Multip = 1/dVoltage
                SetStatus.Execute(oStaExtMea, 0, 1)    # set status to write (PF -> OPC)
                oStaExtMea.pCalObj = oTerminal
                oStaExtMea.varCal = 'm:max_v'
                oStaExtMea.pCalObjSim = oTerminal
                oStaExtMea.varCalSim = 'm:max_v'
                oStaExtMea.i_dat = 3    # set type to real

                sTagId = '%s%s%s%s_VMAX_RES' % (sTagPrefix, sStation, sSeparator, sBaseTag)
                sTagId = ReplaceInvalidChars.Execute(sTagId)
                oStaExtMea.sTagID = sTagId
                oStaExtMea.for_name = sTagId

                iCounter += 1

        resList = IsContainedInDesc.Execute(oCubicle, 'LoadingMea')
        if resList[0]:
            # create measurement (StaExtdatmea) for loading output
            if resList[2]:
                oStaExtMea = oCubicle.CreateObject('StaExtdatmea', 'Ld_', sStation, '_', sBaseName, '_Res')
                if iDebug:
                    pfApp.PrintInfo("%s - Create measurement %s in cubicle %s." % (script.loc_name, oStaExtMea, oCubicle))

                SetStatus.Execute(oStaExtMea, 0, 1)    # set status to write (PF -> OPC)
                oStaExtMea.pCalObj = oComponent
                oStaExtMea.varCal = 'c:loading'
                oStaExtMea.pCalObjSim = oComponent
                oStaExtMea.varCalSim = 'c:loading'
                oStaExtMea.i_dat = 3    # set type to real

                sTagId = '%s%s%s%s_LD_RES' % (sTagPrefix, sStation, sSeparator, sBaseTag)
                sTagId = ReplaceInvalidChars.Execute(sTagId)
                oStaExtMea.sTagID = sTagId
                oStaExtMea.for_name = sTagId

                iCounter += 1

        resList = IsContainedInDesc.Execute(oCubicle, 'maxLoadingMea')
        if resList[0]:
            # create measurement (StaExtdatmea) for maxLoading output
            if resList[2]:
                oStaExtMea = oCubicle.CreateObject('StaExtdatmea', 'MxL_', sStation, '_', sBaseName, '_Res')
                if iDebug:
                    pfApp.PrintInfo("%s - Create measurement %s in cubicle %s." % (script.loc_name, oStaExtMea, oCubicle))

                SetStatus.Execute(oStaExtMea, 0, 1)    # set status to write (PF -> OPC)
                oStaExtMea.pCalObj = oComponent
                oStaExtMea.varCal = 'c:maxLoading'
                oStaExtMea.pCalObjSim = oComponent
                oStaExtMea.varCalSim = 'c:maxLoading'
                oStaExtMea.i_dat = 3    # set type to real

                sTagId = '%s%s%s%s_MXL_RES' % (sTagPrefix, sStation, sSeparator, sBaseTag)
                sTagId = ReplaceInvalidChars.Execute(sTagId)
                oStaExtMea.sTagID = sTagId
                oStaExtMea.for_name = sTagId

                iCounter += 1

    # debug output: summary
    if iDebug:
        pfApp.PrintInfo("%s - Create %d *.{StaExtpmea,StaExtqmea,StaExtvmea,StaExtdatmea} objects." % (script.loc_name, iCounter))

    # return the number of created measurements
    return iCounter


if __name__ == "__main__":
    PF_APP = powerfactory.GetApplication()     # @UndefinedVariable
    SCRIPT = PF_APP.GetCurrentScript()
    S_TAG_PREFIX = SCRIPT.sTagPrefix if hasattr(SCRIPT, 'sTagPrefix') else 'PF.'
    S_SEPARATOR = SCRIPT.sSeparator if hasattr(SCRIPT, 'sSeparator') else ','
    I_ABSOLUTE_VALUES = int(SCRIPT.iAbsoluteValues) if hasattr(SCRIPT, 'iAbsoluteValues') else 1
    I_DEBUG = int(SCRIPT.iDebug) if hasattr(SCRIPT, 'iDebug') else 0
    Execute(PF_APP, S_TAG_PREFIX, S_SEPARATOR, I_ABSOLUTE_VALUES, I_DEBUG)
    PF_APP = None
