///
/// @file OutputWindow.hpp  PowerFactory API
///
/// @author Christoph Wolter
///
#pragma once

#include "../ExportImport.hpp"

namespace api { namespace v1 {

  /// Wrapper for PowerFactory's output window
  class DllExportImport OutputWindow
  {
  public:

    /// Message types supported by the print function
    enum MessageType
    {
      M_PLAIN = 0, ///message not prepended by any text
      M_ERROR = 1, ///message prepended by error prefix, will also popup as error dialog
      M_WARN  = 2, ///message prepended by warning prefix
      M_INFO  = 4 ///message prepended by info prefix
    };

    //--------------------------------------------------------------------
    /// Function to print text into PowerFactory's output window.
    ///
    /// @param[in]    type  => type of message
    /// @param[in]    msg   => message
    //--------------------------------------------------------------------
    virtual void Print(MessageType type, const char* msg) = 0;

    //--------------------------------------------------------------------
    /// Empties the output window. (Contained text is lost.)
    //--------------------------------------------------------------------
    virtual void Clear() = 0;
  };

} } //end namespace api::v1

