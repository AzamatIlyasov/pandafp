///
/// @file Application.hpp  PowerFactory API
///
/// @author Christoph Wolter
///
#pragma once

#include "../ApiValue.hpp"
#include "DataObject.hpp"
#include "../ExportImport.hpp"

namespace api {  namespace v1 {


  class OutputWindow;

  /// Wrapper for PowerFactory application.
  class DllExportImport Application
  {
  public:

    //--------------------------------------------------------------------
    /// Returns the version string for currently running PowerFactory,
    /// e.g. "14.0.505"
    ///
    /// @return string holding version information of PowerFactory application;
    ///                returned string is never null.\n
    ///                String must be released when no longer used.
    //--------------------------------------------------------------------
    virtual const Value* GetVersion() const=0;


    virtual const Value* GetTempDirectory() const=0;

    virtual const Value* GetWorkingDirectory() const=0;

    virtual const Value* GetInstallationDirectory() const=0;

    virtual const Value* GetLanguageCode() const = 0;

    //--------------------------------------------------------------------
    /// Returns an instance of OutputWindow. Each api instance has one
    /// OutputWindow instance.
    ///
    /// @return instance of OutputWindow, never nullptr
    //--------------------------------------------------------------------
    virtual OutputWindow* GetOutputWindow() =0;


    //--------------------------------------------------------------------
    /// Returns current user object.
    ///
    /// @return current user, not nullptr. \n
    ///         Object must be released if no longer in use .
    //--------------------------------------------------------------------
    virtual DataObject* GetCurrentUser() const=0;


    //--------------------------------------------------------------------
    /// Returns currently active PowerFactory project.
    ///
    /// @return active project, nullptr if is there no active project.\n
    ///         Object must be released if no longer in use .
    //--------------------------------------------------------------------
    virtual DataObject* GetActiveProject() const=0;

    //--------------------------------------------------------------------
    /// Returns currently active study case.
    ///
    /// @return active study case, nullptr if there is no active case.\n
    ///         Object must be released if no longer in use.
    //--------------------------------------------------------------------
    virtual DataObject* GetActiveStudyCase() const=0;

    //--------------------------------------------------------------------
    /// Returns all objects that are currently relevant for calculation.
    /// This means, all lines, nodes, switches, transformers,... + types.
    ///
    /// @return objects relevant for calculation, never nullptr. \n
    ///         Container must be released if no longer in use.
    //--------------------------------------------------------------------
    virtual const Value* GetCalcRelevantObjects() const=0;


    //--------------------------------------------------------------------
    /// Returns a class identifier number. Each class name corresponds to
    /// one unique number. The mapping of class name might be different
    /// for different build numbers of PowerFactory, but it is guaranteed
    /// that it will not changed while an Api instance exists.
    /// (Do not keep these numbers static, get them dynamically in your
    /// code using this method.)
    ///
    /// @param[in]    className  => PowerFactory class name
    ///
    /// @return       0, if given name is not a valid class name
    ///               >0, valid class id for given class
    //--------------------------------------------------------------------
    virtual int GetClassId(const char* className) const=0;


    //--------------------------------------------------------------------
    /// Returns a description for a PowerFactory class.
    ///
    /// @param[in]    className  =>  name of a PowerFactory class
    ///
    /// @return       description text, never nullptr; but string is
    ///               empty for invalid class names
    //--------------------------------------------------------------------
    virtual const Value* GetClassDescription(const char* className) const=0;

    enum AttributeMode {
      MODE_DISPLAYED    = 0,
      MODE_INTERNAL     = 1
    };

    //---------------------------------------------------------------------------------------
    /// Changes the way how attribute values are accessed:
    ///     MODE_DISPLAYED = as displayed in PF (unit conversion applied)
    ///     MODE_INTERNAL  = as internally stored
    ///
    /// @author          Christoph Wolter
    ///
    /// @param[in]  mode  =>
    //---------------------------------------------------------------------------------------
    virtual void SetAttributeMode(AttributeMode mode)=0;
    virtual AttributeMode GetAttributeMode() const=0;

    //---------------------------------------------------------------------------------------
    /// Performance optimization: Internally in PF, all objects must be in a special edit
    /// mode before any value can be changed. Switching between this edit mode is quite
    /// time consuming. Setting this write cache option, each object will be set into
    /// edit mode only once and not automatically switched back. (They remain in edit mode.
    /// Optimized for consecutive value modifications.)
    /// The edit mode can be manually left by calling WriteChangesToDb()
    ///
    /// By default, this caching is disabled.
    ///
    /// @author          Christoph Wolter
    ///
    /// @param[in]  enabled  =>
    //---------------------------------------------------------------------------------------
    virtual void SetWriteCacheEnabled(bool enabled)=0;
    virtual bool IsWriteCacheEnabled() const=0;



    //--------------------------------------------------------------------------------
    /// This option allows to change the behavior of creation vs. re-using api::DataObject
    /// instances for identical PowerFactory objects.
    /// When enabled(default) access to the same PowerFactory object will result in usage
    /// of same api::DataObject instance (re-used) until the instance has explicitly been
    /// released via ReleaseObject() call.
    ///
    /// @params[in]  enabled  => enables or disables re-using of api::DataObject instances.
    ///                          This affects the behavior of all api functions returning
    ///                          api::DataObject pointers.
    ///
    /// @return
    //--------------------------------------------------------------------------------
    virtual void SetObjectReusingEnabled(bool enabled)=0;
    virtual bool IsObjectReusingEnabled() const=0;


    //--------------------------------------------------------------------
    /// Returns the information about the type of an attribute.
    ///
    /// @param[in]    attribute  =>  name of an attribute
    ///
    /// @return       type of the attribute \n
    ///               TYPE_INVALID on error (no attribute of that name exists)
    //--------------------------------------------------------------------
    virtual DataObject::AttributeType GetAttributeType(const char* classname, const char* attribute) const=0;


    //--------------------------------------------------------------------------------
    /// Checks whether attribute with given name can be written via the api.
    /// Typical read-only attributes are calculation results.
    /// NB: This function does not check user permissions. This means that write access
    /// can fail even if this functions returns not read-only.
    ///
    /// @param[in]  attribute  =>  name of attribute to check
    ///
    /// @return     true, if attribute exists and can be written via API
    ///             false, otherwise
    //--------------------------------------------------------------------------------
    virtual bool IsAttributeReadOnly(const char* classname, const char* attribute) const=0;


    //--------------------------------------------------------------------
    /// Returns the description of an attribute.
    ///
    /// @param[in]    attribute  =>  attribute name
    /// @param[in]    shortDescription  =>  on true only short description is returned
    ///
    /// @return       nullptr, if given attribute does not exist \n
    ///               description string
    ///               String must be released when no longer used.
    //--------------------------------------------------------------------
    virtual const Value* GetAttributeDescription(const char* classname, const char* attribute, bool shortDescription=false) const=0;


    //--------------------------------------------------------------------
    /// Returns the unit of an attribute, e.g. km, MW...
    ///
    /// @param[in]    attribute  =>  attribute name
    ///
    /// @return       nullptr, if given attribute name does not exist \n
    ///               unit string, empty for attributes that have no unit \n
    ///               String must be released when no longer used.
    //--------------------------------------------------------------------
    virtual const Value* GetAttributeUnit(const char* classname, const char* attribute) const=0;


    virtual void GetAttributeSize(const char* classname, const char* attribute, int& countRows, int& countCols) const=0;

    virtual const Value* Execute(const char* command, const Value* inArgs, int* error=0) =0;


    virtual void DefineTransferAttributes(const char* classname, const char* attributes, int* error=0)=0;


    //---------------------------------------------------------------------------------------
    /// Writes all (in memory) modified objects to database.
    /// @see DataObject::WriteChangesToDb()
    //---------------------------------------------------------------------------------------
    virtual void WriteChangesToDb() =0;
  }; //end class Application

} } //end namespace api::v1

