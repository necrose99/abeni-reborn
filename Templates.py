"""

Add your own eclass templates here. Use this format:


To add a "command":

    parent.AddCommand("inherit kde-base")


To add a variable:

    parent.AddNewVar("VAR_NAME", "value")


To add a function set the body of the function in a variable.
Use \t to indent and triple quotes:

    srcinst = '''
src_install() {
\tmake DESTDIR=${D} install || die
}
'''

    parent.AddFunc("src_install", (srcinst))


Follow the examples below. Make sure you prefix the name
you want in the menu with "my". For instance:

def myGnome(parent):

will show as "Gnome" in the menu.


"""



def myGames(parent):
    """Add games.eclass stuff"""

    parent.AddCommand("inherit games")


    src_compile="""
src_compile() {
\tegamesconf
\temake
}"""

    parent.AddFunc("src_compile", (src_compile))

    src_install="""
src_install() {
\t#make DESTDIR=${D} install || die\
\tegamesinstall || die
\tprepgamesdirs
}"""
    parent.AddFunc("src_install", (src_install))


def myDistutils(parent):
    """Add Python distutils-related variables, inherit etc."""
    # You don't need src_install() with distutils because it gets called automatically.
    # We add it in case they want to add anything to it.

    parent.AddCommand("inherit distutils")

    src_install ="""
src_install() {
\tdistutils_src_install
}"""

    parent.AddFunc("src_install", (src_install))

def myCVS(parent):
    """Add CVS-related variables, inherit etc."""

    src_compile ="""src_compile() {
\texport WANT_AUTOCONF_2_5=1
\tsh autogen.sh
\teconf || die 'configure failed'
\temake || die 'parallel make failed'
}"""

    src_install ="""src_install() {
\teinstall || die 'make install failed'
}"""

    parent.AddNewVar("ECVS_SERVER", "")
    parent.AddNewVar("ECVS_MODULE", "")
    parent.AddNewVar("ECVS_TOD_DIR", "$DIST/")
    parent.AddNewVar("S", "${WORKDIR}/${PN/-cvs/}")
    parent.AddCommand("inherit cvs")
    parent.AddFunc("src_compile", (src_compile))
    parent.AddFunc("src_install", (src_install))
