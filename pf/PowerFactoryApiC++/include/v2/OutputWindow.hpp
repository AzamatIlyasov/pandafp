///
/// @file OutputWindow.hpp  PowerFactory API
///
/// @author Christoph Wolter
///
#pragma once

#include "../ExportImport.hpp"
#include "../ApiValue.hpp"

namespace api { namespace v2 {

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

    //--------------------------------------------------------------------
    /// Returns the content of the output window. (Returned value is a
    /// vector of strings where each message in output window is stored
    /// as one entry.)
    //--------------------------------------------------------------------
    virtual const Value* GetContent() = 0;

    //--------------------------------------------------------------------
    /// Returns the content of the output window filtered by message type.
    /// (Filtered version of GetText())
    ///
    /// @param[in]    filter  => only text from messages of this type will
    ///                          be returned
    //--------------------------------------------------------------------
    virtual const Value* GetContent(MessageType filter) = 0;

    //--------------------------------------------------------------------
    /// Saves the content of current output window to a file.
    /// Possible file formats are html, txt and out. The file format is
    /// derived from the filePath passed to the function.
    ///
    /// @param[in]    filePath  => full file name with path,
    ///                            e.g. d:\data\output.txt
    //--------------------------------------------------------------------
    virtual void Save(const char* filePath) = 0;
  };

} } //end namespace api::v2

