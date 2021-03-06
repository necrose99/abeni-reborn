// -*- C++ -*-
//
// generated by wxGlade HG on Sat May 24 09:10:31 2014
//
// Example for compiling a single file project under Linux using g++:
//  g++ MyApp.cpp $(wx-config --libs) $(wx-config --cxxflags) -o MyApp
//
// Example for compiling a multi file project under Linux using g++:
//  g++ main.cpp $(wx-config --libs) $(wx-config --cxxflags) -o MyApp Dialog1.cpp Frame1.cpp
//

#ifndef GUI_H
#define GUI_H

#include <wx/wx.h>
#include <wx/image.h>
#include "wx/intl.h"

#ifndef APP_CATALOG
#define APP_CATALOG "app"  // replace with the appropriate catalog name
#endif


// begin wxGlade: ::dependencies
#include <wx/splitter.h>
#include <wx/treectrl.h>
#include <wx/statline.h>
#include <wx/tglbtn.h>
#include <wx/notebook.h>
// end wxGlade

// begin wxGlade: ::extracode
// end wxGlade


class MyFrame: public wxFrame {
public:
    // begin wxGlade: MyFrame::ids
    enum {
        mnuNewID = wx.NewId(),
        mnuLoadOverlayID = wx.NewId(),
        mnuLoadID = wx.NewId(),
        mnuSaveID = wx.NewId(),
        mnuDelID = wx.NewId(),
        mnuExportID = wx.NewId(),
        exitID = wx.NewId(),
        mnuFindID = wx.NewId(),
        mnuFindAgainID = wx.NewId(),
        mnuAddFuncID = wx.NewId(),
        mnuLicenseID = wx.NewId(),
        mnuCleanID = wx.NewId(),
        mnuDigestID = wx.NewId(),
        mnuUnpackID = wx.NewId(),
        mnuCompileID = wx.NewId(),
        mnuInstallID = wx.NewId(),
        mnuQmergeID = wx.NewId(),
        mnuEbuildID = wx.NewId(),
        mnuEmergeID = wx.NewId(),
        mnuRepoScanID = wx.NewId(),
        mnuPatchID = wx.NewId(),
        mnuImportID = wx.NewId(),
        mnuDiffID = wx.NewId(),
        mnuRepoFullID = wx.NewId(),
        mnuFileCopyID = wx.NewId(),
        mnuXtermSID = wx.NewId(),
        mnuXtermDID = wx.NewId(),
        mnuXtermCVSID = wx.NewId(),
        self.mnuFullCommitID = wx.NewId(),
        mnuEditID = wx.NewId(),
        mnuViewMetadataID = wx.NewId(),
        mnuViewChangeLogID = wx.NewId(),
        mnuClearLogID = wx.NewId(),
        mnuPrefID = wx.NewId(),
        mnuHelpID = wx.NewId(),
        mnuHelpRefID = wx.NewId(),
        mnuEclassID = wx.NewId(),
        mnuPrivID = wx.NewId(),
        mnuUseID = wx.NewId(),
        mnulocalUseID = wx.NewId(),
        mnuFKEYS_ID = wx.NewId(),
        mnuCVS_ID = wx.NewId(),
        mnuAboutID = wx.NewId(),
        newID = wx.NewId(),
        openID = wx.NewId(),
        openOvlID = wx.NewId(),
        saveID = wx.NewId(),
        editID = wx.NewId(),
        newFuncID = wx.NewId(),
        toolCleanID = wx.NewId(),
        digestID = wx.NewId(),
        unpackID = wx.NewId(),
        compileID = wx.NewId(),
        installID = wx.NewId(),
        qmergeID = wx.NewId(),
        ebuildID = wx.NewId(),
        emergeID = wx.NewId(),
        xtermID = wx.NewId(),
        self.StopID = wx.NewId(),
        treeID = wx.NewId()
    };
    // end wxGlade

    MyFrame(wxWindow* parent, int id, const wxString& title, const wxPoint& pos=wxDefaultPosition, const wxSize& size=wxDefaultSize, long style=wxDEFAULT_FRAME_STYLE);

private:
    // begin wxGlade: MyFrame::methods
    void set_properties();
    void do_layout();
    // end wxGlade

protected:
    // begin wxGlade: MyFrame::attributes
    wxMenuBar* menubar;
    wxStatusBar* statusbar;
    wxToolBar* toolbar;
    wxStaticLine* static_line_2;
    wxButton* button_Category;
    wxTextCtrl* text_ctrl_Category;
    wxStaticText* label_PN;
    wxTextCtrl* text_ctrl_PN;
    wxStaticText* label_PVR;
    wxTextCtrl* text_ctrl_PVR;
    wxToggleButton* button_1;
    wxPanel* panel_cpvr;
    wxStaticLine* static_line_3;
    GentooSTC* STCeditor;
    wxTextCtrl* text_ctrl_log;
    wxPanel* panel_log;
    wxTreeCtrl* tree_ctrl_1;
    wxPanel* window_1_pane_1;
    wx.GenericDirCtrl* explorer;
    wxButton* button_view;
    wxButton* button_edit;
    wxButton* button_patch;
    wxButton* button_delete;
    wxPanel* window_1_pane_2;
    wxSplitterWindow* window_1;
    wxPanel* panel_explorer;
    wxTextCtrl* text_ctrl_environment;
    wxButton* button_env_refresh;
    wxRadioBox* radio_box_env;
    wxPanel* panel_environment;
    wxNotebook* notebook_1;
    wxSplitterWindow* splitter;
    wxPanel* panel_1;
    // end wxGlade
}; // wxGlade: end class


#endif // GUI_H
