///
/// @file Api.hpp  PowerFactory API
///
/// @author Christoph Wolter
///
#pragma once
#include "../ApiValue.hpp"
#include "Application.hpp"
#include "../ExportImport.hpp"

namespace api { namespace v1 {


  class DataObject;

  /// Main Api class
  class DllExportImport Api
  {
  public:

    //--------------------------------------------------------------------
    /// Returns the version number of current api instance.
    ///
    /// @return version of api, e.g. 1.0
    //--------------------------------------------------------------------
    virtual const Value* GetVersion() const=0;


    //--------------------------------------------------------------------
    /// Releases an Api object instance.
    /// All Api object pointers created by the Api must be released
    /// using this function. Calling delete from an external DLL is not
    /// possible as the Api instance has an own memory management.
    ///
    /// @param[in]    object  =>  pointer to an
    ///
    /// @return 0 on success, \n
    ///         >0 on error
    //--------------------------------------------------------------------
    virtual int ReleaseObject(DataObject*& object) =0;


    //---------------------------------------------------------------------------------------
    /// Releases an Api Value object.
    /// Please note that if given object is of type Value::VECTOR, in addtion all contained
    /// Value objects are released too.
    ///
    /// @see also int ReleaseObject(const DataObject* object)
    ///
    /// @param[in]  object  =>  pointer to a Value object
    ///
    /// @return 0 on success, \n
    ///         >0 on error
    //---------------------------------------------------------------------------------------
    virtual int ReleaseValue(const Value*& object) =0;


    //--------------------------------------------------------------------
    /// Returns an instance of the application. There exists one application
    /// object per Api instance. This application object must not be deleted.
    ///
    /// @return pointer to instance of application object \n
    ///         never nullptr
    //--------------------------------------------------------------------
    virtual Application* GetApplication() =0;


    //---------------------------------------------------------------------------------------
    /// Returns true if PowerFactory is in debug mode. False otherwise.
    ///
    /// @return     true if PF is in debug mode, else false
    //---------------------------------------------------------------------------------------
    virtual bool IsDebug() const=0;

  protected:

    //--------------------------------------------------------------------
    /// Constructor.
    //--------------------------------------------------------------------
    Api(){};


    //--------------------------------------------------------------------
    /// Destructor.
    //--------------------------------------------------------------------
    virtual ~Api(){};

  private:

  }; //end of class Api

} } //end namespace api::v1


extern "C" {
  DllExportImport void DestroyApiInstanceV1(api::v1::Api*& api);
  DllExportImport api::v1::Api* CreateApiInstanceV1(const char* username, const char* password, const char* commandLineArguments);
  DllExportImport api::v1::Api* CreateApiInstanceSecuredV1(const char* username, const char* passwordHash, const char* commandLineArguments);
  //deprecated, no longer working
  DllExportImport api::v1::Api* CreateApiInstanceWithTokenV1(const char* token, const char* instanceId);

  typedef api::v1::Api* (__cdecl *CREATEAPI_V1)(const char* username, const char* password, const char* commandLineArguments);
  typedef api::v1::Api* (__cdecl *CREATEAPI_SECURE_V1)(const char* username, const char* passwordHash, const char* commandLineArguments);
  typedef void(__cdecl *DESTROYAPI_V1)(api::v1::Api*&);
}

