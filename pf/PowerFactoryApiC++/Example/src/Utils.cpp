#include "Utils.hpp"
#include "v2/ExitError.hpp"

#include <windows.h>

using std::vector;
using std::string;

typedef api::v2::ExitError ExitError;

extern "C" {
typedef Api* (__cdecl *CREATEAPI)(const char* username, const char* password, const char* commandLineArguments);
typedef void (__cdecl *DESTROYAPI)(Api*&);
}

#undef GetClassName

HINSTANCE dllHandle = NULL;

Api* ApiFixture::instance = 0;;

ApiFixture::ApiFixture()
{
  //create an api instance
  dllHandle = LoadLibrary(TEXT("digapi.dll")); ///< handle to loaded digapi.dll

  if (!dllHandle) {
    return;
  }
  try {
    CREATEAPI createApi = (CREATEAPI)GetProcAddress((struct HINSTANCE__*)dllHandle, "CreateApiInstanceV2");
    std::cout << "Creating API instance..." << std::endl;
    instance = createApi(NULL, NULL, NULL);
  }
  catch(const api::v2::ExitError& ex) {
    std::cout << "API instance creation failed with error code " << ex.GetCode() << std::endl;
    throw;
  }
}

ApiFixture::~ApiFixture()
{
  if (dllHandle) {
    std::cout << "Releasing API instance..." << std::endl;
    DESTROYAPI destroyApi = (DESTROYAPI) GetProcAddress ((struct HINSTANCE__*)dllHandle, "DestroyApiInstanceV2");
    destroyApi(instance);
    instance = NULL;

    FreeLibrary(dllHandle);
    dllHandle = NULL;
  }
}

ValueGuard::~ValueGuard()
{
  if (ApiFixture::GetInstance() && m_val) {
    ApiFixture::GetInstance()->ReleaseValue(m_val);
  }
}


std::vector<DataObject*> Utils::GetChildren(DataObject* parent, std::string classNameFilter)
{
  vector<DataObject*> result;

  ValueGuard children(parent->GetChildren(FALSE));
  for (unsigned int i=0, count = children->VecGetSize(); i < count; ++i) {
    DataObject* child = static_cast<DataObject*>(children->VecGetDataObject(i));
    if (classNameFilter.empty()) {
      result.push_back(child);
    }
    else {
      ValueGuard classname(child->GetClassName());
      if (strcmp(classname->GetString(), classNameFilter.c_str()) == 0) {
        result.push_back(child);
      }
    }
  }

  return result;
}
