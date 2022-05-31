///
/// @file DataObject.hpp  PowerFactory API
///
/// @author Christoph Wolter
///
#pragma once

#include "../ApiValue.hpp"
#include "../ExportImport.hpp"

namespace api {  namespace v2 {


  class DataObject;
 
  /// Wrapper for PowerFactory data objects
  class DllExportImport DataObject
  {
  public:

    ///Data type for attributes
    enum AttributeType {
      TYPE_INVALID      = -1,

      TYPE_INTEGER      = 0,
      TYPE_INTEGER_VEC  = 1,

      TYPE_DOUBLE       = 2,
      TYPE_DOUBLE_VEC   = 3,
      TYPE_DOUBLE_MAT   = 4,

      TYPE_OBJECT       = 5,
      TYPE_OBJECT_VEC   = 6,

      TYPE_STRING       = 7,
      TYPE_STRING_VEC   = 8,

      TYPE_INTEGER64    = 9,
      TYPE_INTEGER64_VEC = 10,
    };


    //--------------------------------------------------------------------
    /// Returns class name of PowerFactory object.
    ///
    /// @return non-empty class name, e.g. ElmTerm, ElmCoup; never nullptr
    //--------------------------------------------------------------------
    virtual const Value* GetClassName() const=0;


    //--------------------------------------------------------------------
    /// Returns the identifier number for the class of current object's
    /// instance.
    /// @see  api::Application::getClassId(const std::string& className)
    ///
    /// @return       class id > 0
    //--------------------------------------------------------------------
    virtual int GetClassId() const=0;


    //--------------------------------------------------------------------
    /// Returns the name of the object. Corresponds to attribute loc_name.
    ///
    /// @return   value of loc_name attribute, never nullptr
    //--------------------------------------------------------------------
    virtual const Value* GetName() const=0;


    //--------------------------------------------------------------------
    /// Returns the full name (full hierarchy path) of the object.
    ///
    /// @return       full name, never nullptr
    //--------------------------------------------------------------------
    virtual const Value* GetFullName(DataObject* relParent=0) const=0;


    //--------------------------------------------------------------------
    /// Returns collection of children for current object.
    ///
    /// @param[in]    recursive  =>  if false, only direct children of current
    ///                              object are returned; \n
    ///                              if true, additionally all children's children
    ///                              plus their children and so on... are returned
    ///
    /// @return       vector of DataObjects (vector<DataObject*>*), never nullptr
    //--------------------------------------------------------------------
    virtual const Value* GetChildren(bool recursive, int classfilter=-1) const =0; //TODO CW: implement classfilter


    //--------------------------------------------------------------------
    /// Returns the parent object.
    ///
    /// @return      parent object; nullptr, if on highest level
    //--------------------------------------------------------------------
    virtual DataObject* GetParent() const=0;


    //--------------------------------------------------------------------
    /// Checks whether object is a network data folder.
    ///
    /// @return      true for network data folder objects, e.g. IntBmu, IntZone...\n
    ///              false, otherwise
    //--------------------------------------------------------------------
    virtual bool IsNetworkDataFolder() const=0;


    //--------------------------------------------------------------------
    /// Checks whether the object is active (depending on currently
    /// activated variation stage)
    ///
    /// @return       true, if currently not active (added in inactive stage
    ///                     or deleted in currently active stage)\n
    ///               false, if object is currently active
    //--------------------------------------------------------------------
    virtual bool IsHidden() const=0;


    //--------------------------------------------------------------------
    /// Checks whether the object is deleted (stored in recycle bin)
    ///
    /// @return       true, if object is deleted and currently stored in
    ///                     recycle bin
    ///               false, otherwise
    //--------------------------------------------------------------------
    virtual bool IsDeleted() const =0;


    //--------------------------------------------------------------------
    /// Returns the information about the type of an attribute.
    ///
    /// @param[in]    attribute  =>  name of an attribute
    ///
    /// @return       type of the attribute \n
    ///               TYPE_INVALID on error (no attribute of that name exists)
    //--------------------------------------------------------------------
    virtual DataObject::AttributeType GetAttributeType(const char* attribute) const=0;


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
    virtual bool IsAttributeReadOnly(const char* attribute) const=0;


    //--------------------------------------------------------------------
    /// Returns the description of an attribute.
    ///
    /// @param[in]    attribute         =>  attribute name
    /// @param[in]    shortDescription  =>  on true only short description is returned
    ///
    /// @return       nullptr, if given attribute does not exist \n
    ///               description string
    ///               String must be released when no longer used.
    //--------------------------------------------------------------------
    virtual const Value* GetAttributeDescription(const char* attribute, bool shortDescription=false) const=0;


    //--------------------------------------------------------------------
    /// Returns the unit of an attribute, e.g. km, MW...
    ///
    /// @param[in]    attribute  =>  attribute name
    ///
    /// @return       nullptr, if given attribute name does not exist \n
    ///               unit string, empty for attributes that have no unit \n
    ///               String must be released when no longer used.
    //--------------------------------------------------------------------
    virtual const Value* GetAttributeUnit(const char* attribute) const=0;

    virtual void GetAttributeSize(const char* attribute, int& countRows, int& countCols) const=0;

    virtual int GetAttributeInt(const char* attribute, int* error=0) const=0;
    virtual int GetAttributeInt(const char* attribute, int row, int col, int* error=0) const=0;

    virtual __int64 GetAttributeInt64(const char* attribute, int* error=0) const=0;
    virtual __int64 GetAttributeInt64(const char* attribute, int row, int col, int* error=0) const=0;

    virtual double GetAttributeDouble(const char* attribute, int* error=0) const=0;
    virtual double GetAttributeDouble(const char* attribute, int row, int col, int* error=0) const=0;

    virtual DataObject* GetAttributeObject(const char* attribute, int* error=0) const=0;
    virtual DataObject* GetAttributeObject(const char* attribute, int row, int* error=0) const=0;

    virtual void SetAttributeObject(const char* attribute, DataObject* obj, int* error=0) =0;
    virtual void SetAttributeObject(const char* attribute, DataObject* obj, int row, int* error=0) =0;

    virtual const Value* GetAttributeString(const char* attribute, int* error=0) const=0;
    virtual const Value* GetAttributeString(const char* attribute, int row, int* error=0) const=0;

    virtual const Value* GetAttributeContainer(const char* attribute, int* error=0) const =0;

    virtual void SetAttributeString(const char* attribute, const char* value, int* error=0) =0;
    virtual void SetAttributeString(const char* attribute, const char* value, int row, int col, int* error=0) =0;

    virtual void SetAttributeDouble(const char* attribute, double value, int* error=0) =0;
    virtual void SetAttributeDouble(const char* attribute, double value, int row, int col, int* error=0) =0;

    virtual void SetAttributeInt(const char* attribute, int value, int* error=0) =0;
    virtual void SetAttributeInt(const char* attribute, int value, int row, int col, int* error=0) =0;

    virtual void SetAttributeInt64(const char* attribute, __int64 value, int* error=0) =0;
    virtual void SetAttributeInt64(const char* attribute, __int64 value, int row, int col, int* error=0) =0;

    virtual void SetAttributeContainer(const char* attribute, const Value* value, int* error=0) =0;

    virtual void ResizeAttribute(const char* attribute, int rowSize, int colSize, int* error=0) =0;

    virtual const Value* GetAttributeNames() const =0;


    virtual DataObject* CreateObject(const char* className, const char* locname) =0;

    virtual void DeleteObject(int* error=0)=0;

    virtual const Value* Execute(const char* command, const Value* inArgs, int* error=0)=0;

    virtual void SetAttributes(const Value* values, int* error=0)=0;
    virtual const Value* GetAttributes(int* error=0) const=0;

    virtual DataObject* CreateObject(const char* classname, const Value* values, int* error=0)=0;

    //---------------------------------------------------------------------------------------
    /// Only required for manually committing changed values (performance optimization).
    /// @see SetWriteCacheEnabled()
    //---------------------------------------------------------------------------------------
    virtual void WriteChangesToDb() =0;


    //--------------------------------------------------------------------------------
    /// Checks whether two api::DataObject instances are wrapping the same PowerFactory
    /// object. (Req. in case of disabling of instance re-usage, see IsObjectReusingEnabled(())
    ///
    /// @params[in]  api::DataObject* other  =>
    ///
    /// @return   true, if this and passed instance are both wrappers for identical
    ///                 PowerFactory object
    ///           false, if wrapped PowerFactory object is different
    //--------------------------------------------------------------------------------
    virtual bool IsSame(const DataObject* other) const = 0;
  }; //end class DataObject

} } //end namespace api::v2


