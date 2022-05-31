///
/// @file ExportImport.hpp  PowerFactory API
///
/// @author Christoph Wolter
///
#ifndef __EXPORTIMPORT_HPP_INCLUDED
#define __EXPORTIMPORT_HPP_INCLUDED

#ifdef DIGAPI
  #define DllExportImport   __declspec( dllexport)
#else
  #define DllExportImport   __declspec( dllimport)
#endif

#endif // __EXPORTIMPORT_HPP_INCLUDED
