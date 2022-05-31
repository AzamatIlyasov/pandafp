///
/// @file ExitError.hpp  PowerFactory API ExitError
///
/// @author Christoph Wolter
///
#pragma once

#include "../ExportImport.hpp"

namespace api { namespace v2 {

/// Exception class thrown when PowerFactor can not be started or crashes
class DllExportImport ExitError
{
public:

  //---------------------------------------------------------------------------------------
  /// Returns the code of the exit error.
  ///
  /// @return >0. A detailed description of all exit errors can be found in the error code reference (see .\\help\\ErrorCodeReference_en.pdf)
  //---------------------------------------------------------------------------------------
  virtual int GetCode() const = 0;

}; //end of class ExitError

} } //end namespace api::v2

