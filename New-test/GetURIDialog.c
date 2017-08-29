<?xml version="1.0" encoding="ANSI_X3.4-1968"?>
<!-- generated by wxGlade HG on Sat May 24 09:06:53 2014 -->

<resource version="2.3.0.1">
    <object class="wxDialog" name="dialog_1" subclass="GetURIDialog">
        <style>wxDEFAULT_DIALOG_STYLE</style>
        <size>407, 146</size>
        <title>Enter URI for package</title>
        <object class="wxBoxSizer">
            <orient>wxVERTICAL</orient>
            <object class="sizeritem">
                <flag>wxTOP|wxBOTTOM|wxEXPAND</flag>
                <border>10</border>
                <object class="wxBoxSizer">
                    <orient>wxHORIZONTAL</orient>
                    <object class="sizeritem">
                        <flag>wxLEFT</flag>
                        <border>4</border>
                        <object class="wxStaticText" name="label_uri">
                            <label>Package URI:</label>
                        </object>
                    </object>
                    <object class="sizeritem">
                        <option>1</option>
                        <flag>wxLEFT</flag>
                        <border>12</border>
                        <object class="wxTextCtrl" name="URI">
                            <size>304, 22</size>
                        </object>
                    </object>
                </object>
            </object>
            <object class="sizeritem">
                <flag>wxTOP|wxBOTTOM|wxEXPAND</flag>
                <border>10</border>
                <object class="wxBoxSizer">
                    <orient>wxHORIZONTAL</orient>
                    <object class="sizeritem">
                        <flag>wxLEFT|wxALIGN_RIGHT</flag>
                        <border>4</border>
                        <object class="wxStaticText" name="label_template">
                            <label>Template:</label>
                        </object>
                    </object>
                    <object class="sizeritem">
                        <option>1</option>
                        <flag>wxLEFT</flag>
                        <border>20</border>
                        <object class="wxComboBox" name="combo_box_1">
                            <style>wxCB_READONLY|wxCB_SORT</style>
                            <selection>0</selection>
                            <content>
                            </content>
                        </object>
                    </object>
                </object>
            </object>
            <object class="sizeritem">
                <flag>wxEXPAND</flag>
                <object class="wxStaticLine" name="static_line_2">
                    <style>wxLI_HORIZONTAL</style>
                </object>
            </object>
            <object class="sizeritem">
                <flag>wxALL|wxEXPAND</flag>
                <border>12</border>
                <object class="wxBoxSizer">
                    <orient>wxHORIZONTAL</orient>
                    <object class="sizeritem">
                        <object class="wxButton" name="button_cancel">
                            <label>Cancel</label>
                        </object>
                    </object>
                    <object class="spacer">
                        <size>20, 20</size>
                    </object>
                    <object class="sizeritem">
                        <object class="wxButton" name="button_ok">
                            <default>1</default>
                        </object>
                    </object>
                </object>
            </object>
        </object>
    </object>
</resource>