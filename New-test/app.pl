#!/usr/bin/perl -w -- 
#
# generated by wxGlade HG on Sat May 24 09:47:28 2014
#
# To get wxPerl visit http://wxPerl.sourceforge.net/
#

# This is an automatically generated file.
# Manual changes will be overwritten without warning!

use Wx 0.15 qw[:allclasses];
use strict;
package MyApp;

use base qw(Wx::App);
use strict;

use MyFrame;

sub OnInit {
    my( $self ) = shift;

    Wx::InitAllImageHandlers();

    my $frame_1 = MyFrame->new();

    $self->SetTopWindow($frame_1);
    $frame_1->Show(1);

    return 1;
}
# end of class MyApp

package main;

unless(caller){
    my $local = Wx::Locale->new("English", "en", "en"); # replace with ??
    $local->AddCatalog("app"); # replace with the appropriate catalog name

    my $app = MyApp->new();
    $app->MainLoop();
}