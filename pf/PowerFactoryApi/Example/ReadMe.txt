DIgSILENT PowerFactory API example

2016-02-18 by CW, DIgSILENT GmbH

This archive contains an example demonstrating the usage of the PowerFactory API.

The example is provided as a standalone executable including the complete source
code as a MS Visual Studio 2015 project.

For running the example, the following steps have to be executed:

  1. Install PowerFactory on your computer
  2. Start PowerFactory manually:
     a) configure the license server if requuired
     b) import the provided DGS export definitions (DGS 5.0 Export Definitions)
        (File -> Import -> Data *dz)
  3. Close PowerFactory
  4. Open the ApiExample.sln in Visual Studio and compile the example for the correct PowerFactory architecture
  5. Copy the file "Example1.dgs" into the PowerFactory installation directory 
  6. Now, the example can be executed. Please pass the name of a valid DGS file 
     and a name of an output DGS file as command line arguments.
     E.g.
     ApiExample.exe /in:Example1.dgs /out:Result.dgs

     
Functionality:

The following actions are performed during the example run:

   a) PowerFactory instance is started (engine mode)
   b) a project is imported from DGS file
   c) a load flow calculation is performed on the imported project
   d) results / parts of the project are exported into an export DGS file
   e) the imported project is deleted and PowerFactory is terminated
   
Further informations are available as code comments in the source files. In order
to compile the sources, the appropriate API header and library files are requried.
Please check the instructions in the src/api subfolder.

