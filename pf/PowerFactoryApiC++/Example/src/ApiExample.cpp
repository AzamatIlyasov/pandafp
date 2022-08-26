///
/// @file ApiExample.cpp  Example demonstrates usage of PowerFactory API
///
/// @author Christoph Wolter
///
#include "v2/Api.hpp" ///< api header
#include "Utils.hpp"
#include <vector>
#include <string>
#include <time.h>

// Api
typedef api::v2::DataObject DataObject;
typedef api::v2::Application Application;
typedef api::v2::Api Api;
typedef api::v2::ExitError ExitError;
using api::Value;

using std::vector;
using std::string;

int RunExample(const char* inputDgsFile, const char* outputDgsFile);
void ParseArguments(int argc /*in*/, char* argv[] /*in*/, const char*& fileIn /*out*/, const char*& fileOut /*out*/);


//--------------------------------------------------------------------------------
/// Entry point for application
///
/// @return     0 on success
///             1 if an error occurred
//--------------------------------------------------------------------------------
int main(int argc, char* argv[])
{
  const char* fileIn(NULL);
  const char* fileOut(NULL);
  ParseArguments(argc, argv, fileIn, fileOut);
  if (!fileIn || !fileOut) {
    std::cout << "Usage: ApiExample.exe /in:DgsInputFile /out:DgsOutputFile" << std::endl;
    return 1;
  }

  int err(0);
  try {
    ApiFixture fixture;

    err = RunExample(fileIn, fileOut);
  }
  catch(const ExitError& ex) {
    err = 1;
    std::cout << "Exception in PowerFactory occured. Code: " << ex.GetCode() << std::endl;
  }
  catch (const std::exception& e) {
    err = 1;
    std::cout << "Exception occurred: " << e.what() << std::endl;
  }

  std::cout << "Done. Example executed." << std::endl;
  system("PAUSE");

  return err;
}


//--------------------------------------------------------------------------------
/// Parses command line arguments
//--------------------------------------------------------------------------------
void ParseArguments(int argc /*in*/, char* argv[] /*in*/, const char*& fileIn /*out*/, const char*& fileOut /*out*/)
{
  for (int i=0; i < argc; ++i) {
    if (!fileIn && strncmp(argv[i], "/in:", 4) == 0) {
      fileIn = argv[i] + 4;
    }
    else if (!fileOut && strncmp(argv[i], "/out:", 5) == 0) {
      fileOut = argv[i] + 5;
    }
  }
}


//--------------------------------------------------------------------------------
/// Searches and returns an IntFolder containing DGS Export Definitions.
/// The folder must be located inside the current user and its name must contain
/// the words 'DGS' and 'Definition'.
///
/// @param[in]  user  =>  current user
///
/// @return     found IntFolder, might be NULL
//--------------------------------------------------------------------------------
DataObject* GetExportDefinitions(DataObject* user)
{
  DataObject* exportDefinitions (NULL);
  for(auto folder : Utils::GetChildren(user, "IntFolder")) {
    ValueGuard name(folder->GetName());
    if (strstr(name->GetString(), "DGS") && strstr(name->GetString(), "Definition")) {
      exportDefinitions = folder;
      break;
    }
  }
  return exportDefinitions;
}


//--------------------------------------------------------------------------------
/// Performs a DGS Import.
///
/// @param[in]  app       =>  application instance
/// @param[in]  filename  =>  name of DGS File
///
/// @return     0 on success,
///             1 on error
//--------------------------------------------------------------------------------
int ImportDgsFile(Application* app, const char* filename)
{
  if (!app || !filename) {
    return 1;
  }

  DataObject* folder = app->GetCurrentUser();

  DataObject* comImport = folder->CreateObject("ComImport", "DGSImport");
  if (!comImport) {
    return 1;
  }

  struct tm newtime;
  time_t now = time(0);
  localtime_s(&newtime, &now);

  char prjname[128];
  strftime(prjname, 128, "%Y%m%d-%H%M%S_Import", &newtime);

  app->DefineTransferAttributes("ComImport", "iopt_prj,targname,dgsFormat,fFile");

  Value args(Value::VECTOR);
  args.VecInsertInteger(0); //into new project
  args.VecInsertString(prjname);
  args.VecInsertString("DGS File");
  args.VecInsertString(filename);

  int error(0);
  comImport->SetAttributes(&args, &error);
  if (error > 0) {
    return 1;
  }

  comImport->Execute("Execute", NULL, &error);
  comImport->DeleteObject(); //clean up
  return error;
}


//--------------------------------------------------------------------------------
/// Performs a load flow calculation for active project.
///
/// @return     0 if calculation was successful
///             1 on error
//--------------------------------------------------------------------------------
int CalculateLoadFlow(Application* app)
{
  auto prj = app->GetActiveProject();
  if (!prj) {
    return 1;
  }

  //run a load flow calculation
  Value comLdfString("ComLdf");
  ValueGuard comLdf (app->Execute("GetCaseObject", &comLdfString));
  static_cast<DataObject*>(comLdf->GetDataObject())->Execute("Execute", NULL);

  if (ValueGuard(app->Execute("IsLdfValid", NULL))->GetInteger() == 0) {
    //calculation was not successful, stop here
    return 1;
  }

  return 0;
}

//--------------------------------------------------------------------------------
/// Performs a DGS export. Further, prior to the export a load flow is calculated.
/// This allows to export calculation results defined in DGS Export Definition.
///
/// @param[in]  app                =>  application instance
/// @param[in]  exportDefinitions  =>  IntFolder holding export definitions
/// @param[in]  filename           =>  output file name
///
/// @return  0 on success,
///          1 on error
//--------------------------------------------------------------------------------
int ExportDgsFile(Application* app, DataObject* exportDefinitions, const char* filename)
{
  if (!app || !exportDefinitions || !filename) {
    return 1;
  }

  //configure export command and execute it
  Value comExportString("ComExport");
  ValueGuard comExport (app->Execute("GetCaseObject", &comExportString));
  app->DefineTransferAttributes("ComExport", "dgsVer,dgsFormat,fFile,pPer");

  int error(0);
  Value atts(Value::VECTOR);
  atts.VecInsertString("V5.00");
  atts.VecInsertString("ASCII File");
  atts.VecInsertString(filename);
  atts.VecInsertDataObject(exportDefinitions);
  static_cast<DataObject*>(comExport->GetDataObject())->SetAttributes(&atts, &error);
  if (error > 0) {
    return 1;
  }

  static_cast<DataObject*>(comExport->GetDataObject())->Execute("Execute", NULL, &error); //execute command

  return error;
}

//--------------------------------------------------------------------------------
/// Main function that demonstrates usage of API by performing the following actions 
///      1. dgs import, 
///      2. ldf calculation, 
///      3. dgs export example.
///
/// @return     0 on success,
///             1 on error
//--------------------------------------------------------------------------------
int RunExample(const char* inputDgsFile, const char* outputDgsFile)
{
  Api* api = ApiFixture::GetInstance(); //ApiFixture is responsible for creation/destruction api instance
  if (!api) {
    std::cout << "Error: API instance not available." << std::endl;
    return 1;
  }

  Application* app = api->GetApplication();

  //check and get DGS variable export configuration
  DataObject* user = app->GetCurrentUser();
  DataObject* exportDefinitions = GetExportDefinitions(user);
  if (!exportDefinitions) {
    std::cout << "Error: DGS Export definitions not available" << std::endl;
    return 1;
  }

  //import DGS
  int err = ImportDgsFile(app, inputDgsFile);
  if (err > 0) {
    std::cout << "Error: DGS import failed" << std::endl;
    return 1;
  }

  //perform a load flow calculation
  err = CalculateLoadFlow(app);
  if (err > 0) {
    std::cout << "Error: Load flow calculation failed" << std::endl;
    return 1;
  }

  //export DGS
  err = ExportDgsFile(app, exportDefinitions, outputDgsFile);
  if (err > 0) {
    std::cout << "Error: DGS export failed" << std::endl;
    return 1;
  }

  //clean up, delete project
  DataObject* prj = app->GetActiveProject();
  if (prj) {
    prj->Execute("Deactivate", NULL);
    prj->DeleteObject();
  }

  return 0;
}
